import request from '@/utils/request'

// 查询模型列表
export function listModel(query) {
    return request({
        url: '/api/model/list',
        method: 'get',
        params: query
    })
}

// 删除模型
export function delModel(id) {
    return request({
        url: '/api/model/' + id,
        method: 'delete'
    })
}

// 获取模型配置
export function getModelConfig(id) {
    return request({
        url: '/api/model/config/' + id,
        method: 'get'
    })
}

// 配置模型参数
export function configureModel(data) {
    return request({
        url: '/api/model/configure',
        method: 'post',
        data: data
    })
}
