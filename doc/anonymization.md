### Anonymization

Get the level of [k-anonymity](https://en.wikipedia.org/wiki/K-anonymity) of a dataframe using the `get_k`function:

```python
from agd_tools import anonymization

iris_anonymized = iris[['Name']]
k = anonymization.get_k(iris_anonymized)
```