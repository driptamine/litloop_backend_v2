def serialize_page(page):
    return {
        'id': page.id,
        'title': page.title,
        'blocks': [
            {
                'id': block.id,
                'content': block.content,
                'order': block.order,
            }
            for block in page.blocks.all()
        ],
        'children': [
            serialize_page(child) for child in page.get_children()
        ]
    }
