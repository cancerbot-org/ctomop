# Third-party acknowledgments

## Lettuce

PROMOP's optional **Semantic retrieval** strategy adapts the filtered pgvector
cosine-neighbour retrieval approach from [Lettuce](https://github.com/Health-Informatics-UoN/lettuce),
developed by University of Nottingham Health Informatics.

Reference revision: `7e8796ace2cbd86490bb077b3300da003c334e50`, specifically
`lettuce/omop/omop_queries.py` (`query_vector`) and
`lettuce/components/embeddings.py`. The adaptation is implemented in
`omop_core/mapping/suggestions.py` (`semantic_candidates`) using Django and
PROMOP's existing embeddings. It does not require a Lettuce server or use
Lettuce's LLM name-generation pipeline.

Copyright (c) 2024 University of Nottingham Health Informatics.

Lettuce is licensed under the MIT License. Its complete copyright, permission,
and warranty notice is reproduced in [licenses/lettuce-MIT.txt](licenses/lettuce-MIT.txt).
Retain that notice when redistributing this adaptation. PROMOP's own license
remains in [LICENSE](LICENSE).
