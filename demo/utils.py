import requests
from data.data_model import init, execute, paths
from settings import max_nodes_per_level, source_template, target_template, entity_url, mention_url, info_url
from baidu import get_baidu_url


def KG_View(entity):
    url = entity_url.format(entity)
    sess = requests.get(url)  # 请求
    text = sess.text  # 获取返回的数据

    response = eval(text)  # 转为字典类型
    knowledge = response['data']
    nodes = []
    if len(knowledge) == 0:
        return []
    baike_url = get_baidu_url(knowledge['entity'])
    source_node = knowledge['entity'] + '\r\n'+ baike_url
    for avp in knowledge['avp']:
        if avp[1] == knowledge['entity']:
            continue
        node = {'source': source_node, 'target': avp[1], 'type': "resolved", 'rela': avp[0]}
        nodes.append(node)
    links = []
    for i in range(len(nodes)):
        node = nodes[i]
        links.append(node)
    print(links)
    return links


def advogato_data_KG_source(kind, entity, level):
    conn, cursor = init()
    sql = source_template.format(entity)
    entity01 = {}
    nodes = []
    cursor.execute(sql)
    results = cursor.fetchall()
    per_level_nodes = 0
    for row in results:
        source_node = row[1]
        target_node = row[2]
        entity01[source_node] = 1   # 表示已经查询过了
        entity01[target_node] = 0   # 表示还未查询
        node = {'source': row[1], 'target': row[2], 'type': "resolved", 'rela': row[3]}
        nodes.append(node)
        per_level_nodes += 1
        if per_level_nodes > max_nodes_per_level:
            break
    helper(entity01, nodes, level-1, conn, cursor)
    return nodes

def helper(entity01, nodes, level, conn, cursor):
    if level <= 0:
        return
    per_level_nodes = 0
    for entity in list(entity01.keys()):
        print(entity)
        used = entity01[entity]
        if used == 1:
            continue
        sql = source_template.format(entity)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            entity01[entity] = 1
            entity01[row[2]] = 0
            # entity01.update({entity:1, row[2]:0})
            node = {'source': row[1], 'target': row[2], 'type': "resolved", 'rela': row[3]}
            nodes.append(node)
            per_level_nodes += 1
            if per_level_nodes > max_nodes_per_level:
                break
    helper(entity01, nodes, level-1, conn, cursor)


def advogato_data_KG_target(kind, entity):
    '''
    这个暂时没什么用
    :param kind:
    :param entity:
    :return:
    '''
    conn, cursor = init()
    if kind == 'source':
        sql = source_template.format(entity)
    else:
        sql = target_template.format(entity)
    cursor.execute(sql)
    results = cursor.fetchall()
    print(len(results))
    nodes = []   # 最终结果
    seconds = []
    cnt = 0
    for row in results:
        node = {'source': row[1], 'target': row[2], 'type': "resolved", 'rela': row[3]}
        nodes.append(node)
        seconds.append(row[2])
        cnt += 1
        if cnt > max_nodes_per_level:
            break
    thirds = []
    cnt = 0
    for source in seconds:
        sql = source_template.format(source)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            node = {'source': row[1], 'target': row[2], 'type': "resolved", 'rela': row[3]}
            nodes.append(node)
            thirds.append(row[2])
            cnt += 1
            if cnt > max_nodes_per_level:
                break
    cnt = 0
    for source in thirds:
        sql = source_template.format(source)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            node = {'source': row[1], 'target': row[2], 'type': "resolved", 'rela': row[3]}
            nodes.append(node)
            cnt += 1
            if cnt > max_nodes_per_level:
                break
    print(nodes)

    return nodes

def mention2entity(mention):
    '''
    获取歧义关系
    :param mention:
    :return:
    '''
    if mention == "习大大":
        nodes = []
        node = {'source': mention, 'target': "习近平", 'type': "resolved", 'rela': '同名'}
        nodes.append(node)
        second_nodes = KG_View("习近平")
        for node in second_nodes:
            nodes.append(node)
        return nodes
    else:
        url =mention_url.format(mention)
        sess = requests.get(url)
        text = sess.text
        entities = eval(text)  #转为字典类型
        print(entities)
        print(entities['data'])
        nodes = []
        for row in entities['data']:
            node = {'source': mention, 'target': row[0], 'type': "resolved", 'rela': '同名'}
            nodes.append(node)
            print("row[0]:", row[0])
            second_nodes = KG_View(row[0])
            for node in second_nodes:
                print(node)
                if node['rela'] == '国籍':
                    continue
                if node['rela'] == '民族':
                    continue
                if node['rela'] == '中文名':
                    continue
                nodes.append(node)
    return nodes


def question2info(question):
    '''
    问答
    :param questtion:
    :return:
    '''
    url = info_url.format(question)
    sess = requests.get(url)
    text = sess.text
    answer = eval(text)
    print(answer)
    return answer

def get_paths(source, target, cutoff):
    return paths(source,target, cutoff)


if __name__ == '__main__':
    # KG_View('习近平')
    # advogato_data_KG_target('raph', "1", 'miguel')
    # mention2entity('马云')
    # path_test()
    # question2info("美国总统是谁？")
    print()