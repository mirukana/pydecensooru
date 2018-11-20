# pydecensooru

[![PyPI downloads](http://pepy.tech/badge/pydecensooru)](
    http://pepy.tech/project/pydecensooru)
[![PyPI version](https://img.shields.io/pypi/v/pydecensooru.svg)](
    https://pypi.org/projects/pydecensooru)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pydecensooru.svg)](
    https://pypi.python.org/pypi/pydecensooru)

A Python module using [Decensooru](https://github.com/friendlyanon/decensooru)
data to automatically fill any Danbooru post's missing info keys.

The Decensooru `id:md5.ext`
[batches](https://github.com/friendlyanon/decensooru/tree/master/batches)
will be silently fetched and kept up-to-date in your user
data directory,  
e.g. *~/.local/share/pydecensooru* on GNU/Linux by default.

Originally developed for transparent usage with
[lunafind](https://github.com/mirukan/lunafind).

## Examples

```python3
>>> import requests                                                                     
>>> from pydecensooru import decensor, decensor_iter 

# Decensoring a single post if it needs to be:
>>> p2 = requests.get("https://danbooru.donmai.us/posts/2.json").json()
>>> "file_url" in p2
False
>>> p2d = decensor(p2)
>>> "file_url" in p2d
True
>>> p2["file_ext"]
'png'

# Transparently decensoring any post that needs it in a search:
>>> posts = requests.get("https://danbooru.donmai.us/posts.json?tags=id:1..10").json()
>>> print(type(posts), type(posts[0]))
<class 'list'> <class 'dict'>
>>> "file_url" in posts[-2]
False
>>> posts = list(decensor_iter(posts))
>>> "file_url" in posts[-2]
True
```
