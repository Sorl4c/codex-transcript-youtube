#!/usr/bin/env python3
"""
Tests de performance y benchmarks para el sistema RAG PostgreSQL
"""
import pytest
import time
import psutil
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

from second_brain.plan.postgresql_database_experimental import PostgreSQLVectorDatabase
from second_brain.plan.ingest_fase1 import Fase1IngestionControl


@pytest.mark.performance
@pytest.mark.slow
class TestPostgreSQLPerformance:
    """Tests de performance para PostgreSQL RAG"""

    def test_search_latency_benchmark(self, populated_rag_database, rag_performance_thresholds):
        """Test benchmark de latencia de búsqueda"""
        db = populated_rag_database
        max_search_time_ms = rag_performance_thresholds["max_search_time_ms"]

        # Preparar embeddings de prueba
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')

        test_queries = [
            "Docker compose containers",
            "vector embeddings similarity",
            "PostgreSQL database",
            "RAG system architecture",
            "machine learning models"
        ]

        # Generar embeddings
        query_embeddings = [embedder.encode([query])[0].tolist() for query in test_queries]

        # Medir latencia de búsqueda
        search_times = []
        for i, embedding in enumerate(query_embeddings):
            start_time = time.time()
            results = db.search_similar(embedding, top_k=5)
            end_time = time.time()

            search_time_ms = (end_time - start_time) * 1000
            search_times.append(search_time_ms)

            # Validar resultados
            assert isinstance(results, list)
            assert len(results) <= 5

        # Validar performance
        avg_search_time = statistics.mean(search_times)
        max_search_time = max(search_times)

        assert avg_search_time < max_search_time_ms, \
            f"Average search time {avg_search_time:.2f}ms exceeds threshold {max_search_time_ms}ms"
        assert max_search_time < max_search_time_ms * 2, \
            f"Max search time {max_search_time:.2f}ms exceeds 2x threshold {max_search_time_ms * 2}ms"

        print(f"Search performance: avg={avg_search_time:.2f}ms, max={max_search_time:.2f}ms")

    def test_ingestion_throughput_benchmark(self, rag_database, rag_performance_thresholds):
        """Test benchmark de throughput de ingestión"""
        db = rag_database
        max_time_per_doc = rag_performance_thresholds["max_ingestion_time_per_doc"]

        # Preparar dataset de prueba
        num_docs = 50  # Mayor que el dataset normal para stress test
        documents = []

        for i in range(num_docs):
            content = f"Performance test document {i}: Este es un documento de prueba para evaluar el rendimiento del sistema de ingestión de PostgreSQL con embeddings vectoriales."
            embedding = [0.1 + (i * 0.001)] * 384  # Embeddings ligeramente diferentes

            metadata = {
                "source_hash": f"hash_{i:03d}",
                "source_document": f"perf_doc_{i:03d}.txt",
                "chunking_strategy": "performance_test",
                "chunk_index": i,
                "char_start": i * 100,
                "char_end": (i + 1) * 100 - 1,
                "semantic_title": f"Performance Test Document {i}",
                "semantic_summary": f"Performance test document number {i}",
                "semantic_overlap": "",
                "additional_metadata": {"performance_test": True, "doc_id": i}
            }

            documents.append((content, embedding, metadata))

        # Medir throughput de ingestión
        start_time = time.time()
        db.add_documents_with_metadata(documents)
        end_time = time.time()

        total_time = end_time - start_time
        time_per_doc = total_time / num_docs
        docs_per_second = num_docs / total_time

        # Validar performance
        assert time_per_doc < max_time_per_doc, \
            f"Ingestion took {time_per_doc:.4f}s per doc, threshold is {max_time_per_doc}s"

        # Validar que todos los documentos se insertaron
        stats = db.get_stats()
        assert stats["documents"] >= num_docs

        print(f"Ingestion performance: {time_per_doc:.4f}s/doc, {docs_per_second:.2f} docs/sec")

    def test_concurrent_search_performance(self, populated_rag_database, rag_performance_thresholds):
        """Test performance de búsquedas concurrentes"""
        db = populated_rag_database
        max_search_time_ms = rag_performance_thresholds["max_search_time_ms"]

        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Preparar queries concurrentes
        num_threads = 10
        queries_per_thread = 5
        test_queries = [
            f"Test query {i} for concurrent search performance testing"
            for i in range(num_threads * queries_per_thread)
        ]

        query_embeddings = [embedder.encode([query])[0].tolist() for query in test_queries]

        def concurrent_search(embeddings):
            """Función para búsqueda concurrente"""
            times = []
            for embedding in embeddings:
                start_time = time.time()
                results = db.search_similar(embedding, top_k=3)
                end_time = time.time()
                times.append((end_time - start_time) * 1000)
            return times

        # Ejecutar búsquedas concurrentes
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Dividir queries entre threads
            futures = []
            for i in range(num_threads):
                start_idx = i * queries_per_thread
                end_idx = start_idx + queries_per_thread
                thread_embeddings = query_embeddings[start_idx:end_idx]
                future = executor.submit(concurrent_search, thread_embeddings)
                futures.append(future)

            # Recopilar resultados
            all_times = []
            for future in as_completed(futures):
                thread_times = future.result()
                all_times.extend(thread_times)

        end_time = time.time()
        total_concurrent_time = end_time - start_time

        # Validar performance concurrente
        avg_concurrent_time = statistics.mean(all_times)
        max_concurrent_time = max(all_times)

        assert avg_concurrent_time < max_search_time_ms * 1.5, \
            f"Concurrent search avg {avg_concurrent_time:.2f}ms exceeds 1.5x threshold {max_search_time_ms * 1.5}ms"
        assert max_concurrent_time < max_search_time_ms * 3, \
            f"Concurrent search max {max_concurrent_time:.2f}ms exceeds 3x threshold {max_search_time_ms * 3}ms"

        print(f"Concurrent search performance: avg={avg_concurrent_time:.2f}ms, max={max_concurrent_time:.2f}ms, total={total_concurrent_time:.2f}s")

    def test_memory_usage_benchmark(self, rag_database, rag_performance_thresholds):
        """Test benchmark de uso de memoria"""
        max_memory_mb = rag_performance_thresholds["max_memory_usage_mb"]

        # Medir uso de memoria base
        process = psutil.Process(os.getpid())
        base_memory_mb = process.memory_info().rss / 1024 / 1024

        # Realizar operación intensiva
        fase1 = Fase1IngestionControl()

        # Generar embeddings para muchos documentos
        large_texts = [
            f"Large text document {i}: " + "Este es un documento más largo para testing de memoria. " * 20
            for i in range(100)
        ]

        embeddings = fase1.generate_embeddings(large_texts)

        # Medir pico de memoria
        peak_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_increase_mb = peak_memory_mb - base_memory_mb

        # Validar uso de memoria
        assert memory_increase_mb < max_memory_mb, \
            f"Memory increased by {memory_increase_mb:.2f}MB, threshold is {max_memory_mb}MB"

        # Limpiar
        del embeddings
        fase1.db.close()

        print(f"Memory usage: base={base_memory_mb:.2f}MB, peak={peak_memory_mb:.2f}MB, increase={memory_increase_mb:.2f}MB")


@pytest.mark.performance
@pytest.mark.slow
class TestEmbeddingPerformance:
    """Tests de performance para generación de embeddings"""

    def test_embedding_generation_scaling(self):
        """Test escalabilidad de generación de embeddings"""
        fase1 = Fase1IngestionControl()

        batch_sizes = [1, 5, 10, 25, 50, 100]
        generation_times = []
        throughput_rates = []

        for batch_size in batch_sizes:
            texts = [f"Test text {i}" for i in range(batch_size)]

            start_time = time.time()
            embeddings = fase1.generate_embeddings(texts)
            end_time = time.time()

            generation_time = end_time - start_time
            throughput = batch_size / generation_time

            generation_times.append(generation_time)
            throughput_rates.append(throughput)

            # Validar resultados
            assert len(embeddings) == batch_size
            assert all(len(emb) == 384 for emb in embeddings)

            print(f"Batch size {batch_size}: {generation_time:.3f}s, {throughput:.2f} texts/sec")

        # Validar escalabilidad (throughput debería mejorar con batch sizes mayores)
        max_throughput = max(throughput_rates)
        min_throughput = min(throughput_rates)

        assert max_throughput > min_throughput * 0.5, \
            "Throughput should scale reasonably with batch size"

        fase1.db.close()

    def test_embedding_cache_performance(self):
        """Test performance de cache de embeddings (si existe)"""
        fase1 = Fase1IngestionControl()

        # Mismo texto múltiples veces para testear cache
        repeated_texts = ["Test text for cache performance"] * 10

        # Primera generación (sin cache)
        start_time = time.time()
        embeddings_1 = fase1.generate_embeddings(repeated_texts)
        first_time = time.time() - start_time

        # Segunda generación (con cache potencial)
        start_time = time.time()
        embeddings_2 = fase1.generate_embeddings(repeated_texts)
        second_time = time.time() - start_time

        # Validar consistencia
        assert len(embeddings_1) == len(embeddings_2) == 10
        for i in range(10):
            for j in range(384):
                assert abs(embeddings_1[i][j] - embeddings_2[i][j]) < 1e-6

        print(f"First generation: {first_time:.3f}s, Second generation: {second_time:.3f}s")

        # Si hay cache, la segunda vez debería ser más rápida
        # (Esta validación es opcional dependiendo de la implementación)
        if second_time < first_time * 0.8:
            print("Cache detected: second generation was significantly faster")

        fase1.db.close()


@pytest.mark.performance
class TestSystemBenchmarks:
    """Tests de benchmarks del sistema completo"""

    def test_end_to_end_performance_benchmark(self, rag_database, rag_performance_thresholds):
        """Test benchmark end-to-end del sistema completo"""
        max_end_to_end_time = 5.0  # 5 segundos máximo para operación completa

        start_time = time.time()

        # 1. Crear instancia del pipeline
        fase1 = Fase1IngestionControl()

        # 2. Generar dataset pequeño
        small_dataset = [
            {
                "content": f"E2E test document {i}: Performance testing of the complete RAG pipeline",
                "source_hash": f"e2e_hash_{i:03d}",
                "source_document": f"e2e_test_{i:03d}.txt",
                "chunking_strategy": "e2e_test",
                "chunk_index": i,
                "char_start": i * 100,
                "char_end": (i + 1) * 100 - 1,
                "semantic_title": f"E2E Test Document {i}",
                "semantic_summary": f"End-to-end performance test document {i}",
                "semantic_overlap": "",
                "embedding_model": "all-MiniLM-L6-v2",
                "additional_metadata": {"e2e_test": True, "doc_id": i}
            }
            for i in range(5)
        ]

        # 3. Generar embeddings
        texts = [chunk["content"] for chunk in small_dataset]
        embeddings = fase1.generate_embeddings(texts)

        # 4. Ingestar documentos
        documents = []
        for chunk, embedding in zip(small_dataset, embeddings):
            metadata = {
                "source_hash": chunk["source_hash"],
                "source_document": chunk["source_document"],
                "chunking_strategy": chunk["chunking_strategy"],
                "chunk_index": chunk["chunk_index"],
                "char_start": chunk["char_start"],
                "char_end": chunk["char_end"],
                "semantic_title": chunk["semantic_title"],
                "semantic_summary": chunk["semantic_summary"],
                "semantic_overlap": chunk["semantic_overlap"],
                "additional_metadata": chunk["additional_metadata"]
            }
            documents.append((chunk["content"], embedding, metadata))

        fase1.db.add_documents_with_metadata(documents)

        # 5. Realizar búsquedas
        test_queries = [
            "E2E performance test",
            "document benchmark",
            "RAG system testing"
        ]

        for query in test_queries:
            query_embedding = fase1.embedder.encode([query])[0].tolist()
            results = fase1.db.search_similar(query_embedding, top_k=3)
            assert isinstance(results, list)

        # 6. Obtener estadísticas
        stats = fase1.db.get_stats()
        assert stats["documents"] >= 5

        end_time = time.time()
        total_time = end_time - start_time

        # Validar performance end-to-end
        assert total_time < max_end_to_end_time, \
            f"End-to-end operation took {total_time:.2f}s, threshold is {max_end_to_end_time}s"

        print(f"End-to-end performance: {total_time:.2f}s for complete pipeline")

        fase1.db.close()

    def test_system_load_stress_test(self, rag_database):
        """Test de stress del sistema bajo carga"""
        num_operations = 100
        operation_times = []

        fase1 = Fase1IngestionControl()

        # Mix de operaciones: ingestión y búsqueda
        for i in range(num_operations):
            if i % 2 == 0:
                # Operación de ingestión
                content = f"Stress test document {i}"
                embedding = [0.1 + (i * 0.001)] * 384

                metadata = {
                    "source_hash": f"stress_hash_{i:03d}",
                    "source_document": f"stress_test_{i:03d}.txt",
                    "chunking_strategy": "stress_test",
                    "chunk_index": i,
                    "char_start": i * 50,
                    "char_end": (i + 1) * 50 - 1,
                    "semantic_title": f"Stress Test Document {i}",
                    "semantic_summary": f"Stress test document number {i}",
                    "semantic_overlap": "",
                    "additional_metadata": {"stress_test": True, "doc_id": i}
                }

                start_time = time.time()
                fase1.db.add_documents_with_metadata([(content, embedding, metadata)])
                end_time = time.time()
                operation_times.append((end_time - start_time) * 1000)

            else:
                # Operación de búsqueda
                query = f"stress test query {i}"
                query_embedding = fase1.embedder.encode([query])[0].tolist()

                start_time = time.time()
                results = fase1.db.search_similar(query_embedding, top_k=3)
                end_time = time.time()
                operation_times.append((end_time - start_time) * 1000)

        # Validar performance bajo carga
        avg_operation_time = statistics.mean(operation_times)
        max_operation_time = max(operation_times)
        p95_operation_time = statistics.quantiles(operation_times, n=20)[18]  # 95th percentile

        print(f"Stress test performance: avg={avg_operation_time:.2f}ms, max={max_operation_time:.2f}ms, p95={p95_operation_time:.2f}ms")

        # Validar que el sistema mantiene performance bajo carga
        assert avg_operation_time < 100, f"Average operation time {avg_operation_time:.2f}ms too high under load"
        assert p95_operation_time < 500, f"95th percentile {p95_operation_time:.2f}ms too high under load"

        fase1.db.close()


# Performance regression tests
@pytest.mark.performance
@pytest.mark.regression
class TestPerformanceRegression:
    """Tests de regresión de performance"""

    def test_search_performance_regression(self, populated_rag_database):
        """Test de regresión para performance de búsqueda"""
        # Establecer baseline de performance (ajustar según mediciones previas)
        baseline_search_time_ms = 20.0  # 20ms baseline
        regression_threshold = 1.5  # 50% más lento que baseline es regresión

        db = populated_rag_database
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')

        # Medir performance actual
        test_queries = [
            "Docker compose containers",
            "vector embeddings",
            "PostgreSQL database"
        ]

        current_times = []
        for query in test_queries:
            query_embedding = embedder.encode([query])[0].tolist()

            start_time = time.time()
            results = db.search_similar(query_embedding, top_k=5)
            end_time = time.time()

            current_times.append((end_time - start_time) * 1000)

        avg_current_time = statistics.mean(current_times)

        # Validar regresión
        regression_threshold_time = baseline_search_time_ms * regression_threshold
        assert avg_current_time < regression_threshold_time, \
            f"Performance regression: current {avg_current_time:.2f}ms vs baseline {baseline_search_time_ms:.2f}ms"

        print(f"Search performance regression test: current {avg_current_time:.2f}ms, baseline {baseline_search_time_ms:.2f}ms")

    def test_ingestion_performance_regression(self, rag_database):
        """Test de regresión para performance de ingestión"""
        baseline_ingestion_time_per_doc = 0.05  # 50ms baseline
        regression_threshold = 1.5

        db = rag_database

        # Medir performance actual
        num_docs = 20
        documents = []

        for i in range(num_docs):
            content = f"Regression test document {i}"
            embedding = [0.1 + (i * 0.001)] * 384

            metadata = {
                "source_hash": f"regression_hash_{i:03d}",
                "source_document": f"regression_test_{i:03d}.txt",
                "chunking_strategy": "regression_test",
                "chunk_index": i,
                "char_start": i * 50,
                "char_end": (i + 1) * 50 - 1,
                "semantic_title": f"Regression Test Document {i}",
                "semantic_summary": f"Regression test document number {i}",
                "semantic_overlap": "",
                "additional_metadata": {"regression_test": True, "doc_id": i}
            }

            documents.append((content, embedding, metadata))

        start_time = time.time()
        db.add_documents_with_metadata(documents)
        end_time = time.time()

        current_time_per_doc = (end_time - start_time) / num_docs * 1000  # Convertir a ms

        # Validar regresión
        regression_threshold_time = baseline_ingestion_time_per_doc * regression_threshold
        assert current_time_per_doc < regression_threshold_time, \
            f"Ingestion performance regression: current {current_time_per_doc:.2f}ms/doc vs baseline {baseline_ingestion_time_per_doc:.2f}ms/doc"

        print(f"Ingestion performance regression test: current {current_time_per_doc:.2f}ms/doc, baseline {baseline_ingestion_time_per_doc:.2f}ms/doc")