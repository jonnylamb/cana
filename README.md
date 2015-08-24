Caña
=====

A really simple app for testing conjugations. I originally wrote it
ages ago to test some vocab but that has since been removed because
[Anki](http://ankisrs.net/) is much better. The conjugation testing
part remained because I never found anything quite so simple.

Right now it's heavily specific to Italian. It could probably
relatively easily be updated to work with other Latin languages.

Usage
-----

```
./verb [[[verb1] [verb2]] ...]
```

If no argument is given all the verbs in the `verbs/` folder will be
used in the test. Otherwise just the verbs (from the 'verbs/'
directory) specified will be used. There is currently no way to
specify one mood or tense at runtime.

Adding new verbs
----------------

The `scrape` tool tries to automatically scrape conjugations from
wiktionary. It generally works but it can be fragile and it's advised
to have a look at the file in the `verbs/` directory afterwards.

Why?
----

Why not? I was stuck in a house in [Belmonte in
Sabina](https://it.wikipedia.org/wiki/Belmonte_in_Sabina) back in 2012
with no internet and had to get these verbs learnt.