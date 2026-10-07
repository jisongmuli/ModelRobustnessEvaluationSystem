import request from '@/utils/request'

// 上传数据集
export function uploadDataset(data) {
    return request({
        url: '/api/model/dataset/upload',
        method: 'post',
        data: data,
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

// 获取数据集列表
export function listDataset() {
    return request({
        url: '/api/model/dataset/list',
        method: 'get'
    })
}
