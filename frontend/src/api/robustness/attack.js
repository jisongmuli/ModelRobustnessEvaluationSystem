import request from '@/utils/request'

// 获取支持的攻击类型
export function getSupportedAttacks() {
    return request({
        url: '/api/attacks/supported',
        method: 'get'
    })
}

// 启动攻击测试
export function startAttack(data) {
    return request({
        url: '/api/attack/start',
        method: 'post',
        data: data
    })
}

// 查询任务进度
export function getAttackStatus(taskId) {
    return request({
        url: '/api/attack/status/' + taskId,
        method: 'get'
    })
}

// 获取评估结果
export function getAttackResult(taskId) {
    return request({
        url: '/api/attack/result/' + taskId,
        method: 'get'
    })
}

// 获取任务列表
export function getAttackTaskList(query) {
    return request({
        url: '/api/attack/tasks',
        method: 'get',
        params: query
    })
}

// 删除任务
export function deleteAttackTask(taskId) {
    return request({
        url: '/api/attack/task/' + taskId,
        method: 'delete'
    })
}
