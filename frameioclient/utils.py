def stream(func, page=1, page_size=20):
    """
    Accepts a lambda of a call to a client list method, and streams the results until
    the list has been exhausted

    :Args:
        fun (function): A 1-arity function to apply during the stream

        Example:: 
            stream(lambda pagination: client.get_collaborators(project_id, **pagination))
    """
    total_pages = page
    while page <= total_pages:
        result_list = func(page=page, page_size=page_size)
        total_pages = result_list.total_pages
        for res in result_list:
            yield res

        page += 1