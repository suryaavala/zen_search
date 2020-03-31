### Approach

1.  Every `entity` (user, ticket, organisation) is represented by their own class with objects of this class representing individual items.
    1. example each `user` is a dictionary like `{ "_id": "", "url": "", "external_id": "", ...}`
2.  Keeps all these objects in memory all the time (since the data is supposed to fit in memory according to the specs)
3.  And each of these entities have multiple searchable indexes, an index is built for each searchable field
    1. Indexes are hashtables with value of the field as the key in the hash table and the object representing the item as its value
    2. example `users` has indexes on `_id, url, external_id, created_at, etc`; example `_id` index could look like `{1: <entry pointing to user dict with id 1>}`
4.  Search on an entity triggers search for results of that entity type and additional searches in other entities (based on related keys)
    1. example, search on `user._id` triggers a search on `ticket.submitter_id == user._id && ticket.assignee_id == user._id` and `org.id == user.organization_id`

#### Improvements / Things to think about

    1. Instead of linking the entire data element to the index we could just link the primary key and still be able to do constant time searches!
    2. How do insertions / deletions and updates work after indices are built? Maybe add functionality to do that if time permits - Assumption 1
    3. How does search work with multiple constrains? example: search for users who have a tag "Springville", in locale "en-AU", in timezone "Italy"? - Assumption 2
    4. Building index for the primary key as well, which is redundant
    5. Don't have to build indices on fields that are going to be unique

#### Assumptions

    0. "_id" field in each of Users, Organizations and Tickets is unique and it is treated as primary key
    1. All the data is loaded at the beginning
    2. We can only search using one search term at a time
    3. Structure of users, organisation and tickets remain the same as the ones given in spec data files and  remain uniform through out in a file. - structures that are even further nested are not dealt with
       1. users: {<class 'numpy.int64'>, <class 'numpy.float64'>, <class 'numpy.bool_'>, <class 'bool'>, <class 'str'>, <class 'list'>
       2. tickets: {<class 'numpy.int64'>, <class 'numpy.float64'>, <class 'numpy.bool_'>, <class 'str'>, <class 'list'>}
       3. organizations: {<class 'numpy.int64'>, <class 'numpy.bool_'>, <class 'str'>, <class 'list'>}
    4. The only mandatory field we need in these entities is just the "_id". So, if a user doesn't have a "name", they will not appear in any search results by name, except for *
    5. Data files should be a list of data points. Throw an error otherwise
    6. Values of fields in users, organisations and tickets are hashable

#### Trade offs

    1. Must need to traverse the entire data while building indices
    2. More memory required a multiple indices are kept in memory
    3. Fields with Unhashable values can't be indexed

#### Alternative Approaches

- Load everything into a pandas dataframe and use pandas [internals](https://stackoverflow.com/a/49937318/6318316) to query/search
- Maybe SQL Lite given it's [performance benchmark](https://blog.thedataincubator.com/2018/05/sqlite-vs-pandas-performance-benchmarks/)
