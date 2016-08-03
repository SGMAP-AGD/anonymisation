### Anonymisation

Obtenir le niveau [k-anonymity](https://en.wikipedia.org/wiki/K-anonymity) d'un dataframe en utilisant la fonction  `get_k`:

```python
from agd_tools import anonymization

iris_anonymized = iris[['Name']]
k = anonymization.get_k(iris_anonymized)
```

