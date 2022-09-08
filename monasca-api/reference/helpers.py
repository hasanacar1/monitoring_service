import falcon

def get_x_tenant_or_tenant_id(http_request, delegate_authorized_rules_list):
    params = falcon.uri.parse_query_string(http_request.query_string)
    print(params)
    if 'tenant_id' in params:
        tenant_id = params['tenant_id']
    
        for rule in delegate_authorized_rules_list:
            try:
                http_request.can(rule)
                return tenant_id
            except Exception as ex:
                print(ex)

    return http_request.project_id