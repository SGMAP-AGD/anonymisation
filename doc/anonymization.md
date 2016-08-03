### Anonymisation

Obtenir le niveau de [k-anonymat](https://en.wikipedia.org/wiki/K-anonymity) d'un dataframe en utilisant la fonction  `get_k`:

```python
from agd_tools import anonymization

iris_anonymized = iris[['Name']]
k = anonymization.get_k(iris_anonymized)
```

K-anonymiser de façon locale un dataframe en utilisant la fonction `local_aggregation` :

```python
from agd_tools import anonymization

k = 5 
var = dataframe.columns.tolist()
local_aggregation(dataframe.copy(), k, var, method = 'regroup')
```
