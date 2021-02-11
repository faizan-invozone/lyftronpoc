from transformation import Recod

record = Recod()

### Insert Operation ###
# insert_status = record.insert('wp_commentmeta', values={'meta_id': 1001, 'comment_id': 100, 'meta_key': 'testing purpose only'})
# print(insert_status)


### Read Operation ###

# results = record.read('wp_commentmeta', limit=10, where={'meta_id': 1001})
# for result in results:
#     print(result)


### Update Operation ###

# update_results = record.update('wp_commentmeta', values={'meta_value': 123}, where={'meta_id': 1001})
# print(update_results)


### delete operation ###

delete_results = record.delete('wp_commentmeta', where={'meta_id': 1001})
print(delete_results)
