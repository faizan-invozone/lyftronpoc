from transformation import Recod

record = Recod()

record.read('wp_commentmeta', limit=10, where={'meta_id': 1001})

#record.insert('wp_commentmeta', values={'meta_id':1001, 'comment_id': 100, 'meta_key': 'testing only'})

#record.update('wp_commentmeta', values={'meta_value': 12312312}, where={'meta_id': 1001})

#record.delete('wp_commentmeta', where={'meta_id': 1001})