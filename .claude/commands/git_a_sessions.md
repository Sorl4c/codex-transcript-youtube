# /git_a_sessions
Analiza commits de los últimos {{days|3}} días.
Para cada grupo de cambios, crea/actualiza un `.md` en `.claude/sessions/`:
`{{commit_date}}--{{slug top_scope}}.md`

Contenido:
# Cambios del {{commit_date}}
**Commits incluidos:** {{short_hashes}}
**Resumen de cambios:** bullets de 1 línea por commit
**Archivos modificados:** lista breve
**Notas técnicas:** solo si hay puntos importantes

Ignora refactors triviales y cambios de formato.