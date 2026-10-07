<template>
  <div class="app-container home">
    <section class="intro">
      <span class="eyebrow">对抗攻击 · 图像分类</span>
      <h1>模型鲁棒性测试平台</h1>
      <p>上传模型权重，选择真实图像数据，对比攻击前后的表现。</p>
      <el-button type="primary" @click="$router.push('/robustness/model')">管理模型</el-button>
      <el-button @click="$router.push('/robustness/attack')">开始评测</el-button>
    </section>
    <el-row :gutter="20">
      <el-col v-for="step in steps" :key="step.title" :xs="24" :sm="8">
        <el-card class="step" shadow="never">
          <span class="number">{{ step.number }}</span>
          <h2>{{ step.title }}</h2>
          <p>{{ step.description }}</p>
          <router-link :to="step.path">{{ step.action }} →</router-link>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="notes" shadow="never">
      <h2>让结果可以复现</h2>
      <ul>
        <li>上传训练后的 state_dict 权重，确认类别数量与标签顺序；权重不完整时会停止评测。</li>
        <li>标准化方式必须和训练时一致。图像扰动按 0–1 像素范围计算，例如 8 / 255 ≈ 0.0314。</li>
        <li>自定义数据集使用 ZIP，每个类别一个目录。下载失败会明确报错。</li>
        <li>任务记录数据来源、标准化方式与随机种子；执行期间可以到任务列表查看状态。</li>
      </ul>
      <router-link to="/help/guide">查看使用指南 →</router-link>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Index',
  data() {
    return {
      steps: [
        { number: '01', title: '准备模型', description: '上传权重并检查架构、输入大小和分类头。', action: '前往模型管理', path: '/robustness/model' },
        { number: '02', title: '设置攻击', description: '选择数据、攻击方法、扰动大小、标准化与种子。', action: '创建评测任务', path: '/robustness/attack' },
        { number: '03', title: '查看结果', description: '对比准确率、攻击成功率与图像扰动指标。', action: '查看任务列表', path: '/robustness/task' }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.home { max-width: 1250px; margin: 0 auto; color: #23374d; }
.intro { background: #f0f6ff; border: 1px solid #dce8f8; border-radius: 10px; padding: 32px; margin-bottom: 24px; }
.eyebrow { color: #4269a4; font-size: 13px; }
h1 { margin: 14px 0; font-size: 28px; }
h2 { font-size: 18px; margin: 12px 0; }
p { color: #607083; line-height: 1.8; }
.intro p { margin-bottom: 24px; }
.step { min-height: 215px; border-radius: 8px; margin-bottom: 20px; }
.number { color: #7f9fc4; font-size: 24px; font-weight: 600; }
a { color: #2875c7; font-size: 14px; }
.notes { border-radius: 8px; }
ul { padding-left: 22px; color: #607083; line-height: 2; }
@media (max-width: 600px) { .intro { padding: 22px; } h1 { font-size: 23px; } }
</style>
