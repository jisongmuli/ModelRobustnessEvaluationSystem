<template>
  <div class="app-container">
    <el-card v-loading="loading" class="box-card">
      <div slot="header" class="clearfix">
        <span>测试结果</span>
        <div style="float: right;">
          <el-button type="primary" @click="exportToPDF" style="margin-right: 10px;">
            <i class="el-icon-download"></i> 导出PDF
          </el-button>
          <el-button type="text" @click="goBack">返回</el-button>
        </div>
      </div>

      <!-- 基本信息 -->
      <el-descriptions title="任务信息" :column="3" border>
        <el-descriptions-item label="任务ID">{{ result.task_id }}</el-descriptions-item>
        <el-descriptions-item label="模型ID">{{ result.model_id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="result.status === 'completed' ? 'success' : 'danger'">
            {{ result.status === 'completed' ? '已完成' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(result.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDate(result.start_time) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ formatDate(result.end_time) }}</el-descriptions-item>
        <el-descriptions-item v-if="result.summary" label="数据来源">{{ result.summary.dataset_id || '-' }}</el-descriptions-item>
        <el-descriptions-item v-if="result.summary" label="标准化">{{ result.summary.normalization || '-' }}</el-descriptions-item>
        <el-descriptions-item v-if="result.summary" label="随机种子">{{ result.summary.seed === undefined ? '-' : result.summary.seed }}</el-descriptions-item>
      </el-descriptions>

      <!-- 汇总统计 -->
      <el-divider content-position="left">汇总统计</el-divider>
      <el-row :gutter="20" v-if="result.summary" class="summary-row">
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-title">攻击数量</div>
            <div class="stat-value">{{ result.summary.total_attacks }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-title">平均原始准确率</div>
            <div class="stat-value primary">{{ formatPercent(result.summary.avg_clean_accuracy) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-title">平均鲁棒准确率</div>
            <div class="stat-value success">{{ formatPercent(result.summary.avg_robust_accuracy) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box">
            <div class="stat-title">平均攻击成功率</div>
            <div class="stat-value danger">{{ formatPercent(result.summary.avg_attack_success_rate) }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 详细结果表格 -->
      <el-divider content-position="left">详细结果</el-divider>
      <el-table :data="result.metrics" border style="width: 100%">
        <el-table-column label="攻击类型" align="center" prop="attack_type" width="120">
          <template slot-scope="scope">
            <el-tag>{{ scope.row.attack_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="扰动强度 (ε)" align="center" prop="eps" width="120" />
        <el-table-column label="原始准确率" align="center" width="120">
          <template slot-scope="scope">
            {{ formatPercent(scope.row.clean_accuracy) }}
          </template>
        </el-table-column>
        <el-table-column label="鲁棒准确率" align="center" width="120">
          <template slot-scope="scope">
            <span :style="{ color: scope.row.robust_accuracy < scope.row.clean_accuracy * 0.5 ? '#F56C6C' : '#67C23A' }">
              {{ formatPercent(scope.row.robust_accuracy) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="攻击成功率" align="center" width="120">
          <template slot-scope="scope">
            <span :style="{ color: scope.row.attack_success_rate > 0.5 ? '#F56C6C' : '#67C23A' }">
              {{ formatPercent(scope.row.attack_success_rate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="平均 L2 扰动" align="center" prop="avg_perturbation_l2" width="120">
          <template slot-scope="scope">
            {{ formatNumber(scope.row.avg_perturbation_l2) }}
          </template>
        </el-table-column>
        <el-table-column label="平均 L∞ 扰动" align="center" prop="avg_perturbation_linf" width="120">
          <template slot-scope="scope">
            {{ formatNumber(scope.row.avg_perturbation_linf) }}
          </template>
        </el-table-column>
        <el-table-column label="置信度下降" align="center" prop="avg_confidence_drop" width="120">
          <template slot-scope="scope">
            {{ formatNumber(scope.row.avg_confidence_drop) }}
          </template>
        </el-table-column>
        <el-table-column label="样本数" align="center" prop="num_samples" width="100" />
      </el-table>

      <!-- 可视化图表 -->
      <el-divider content-position="left">可视化分析</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="accuracyChart" style="height: 300px;"></div>
        </el-col>
        <el-col :span="12">
          <div ref="perturbationChart" style="height: 300px;"></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { getAttackResult } from "@/api/robustness/attack";


export default {
  name: "ResultView",
  data() {
    return {
      loading: true,
      taskId: "",
      result: {
        task_id: "",
        model_id: "",
        status: "",
        metrics: [],
        summary: null,
        create_time: "",
        start_time: "",
        end_time: ""
      }
    };
  },
  created() {
    this.taskId = this.$route.params.taskId;
    this.loadResult();
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return "-";
      return new Date(dateStr).toLocaleString('zh-CN', { hour12: false });
    },
    formatPercent(val) {
      if (val === undefined || val === null) return "0.00%";
      return (val * 100).toFixed(2) + "%";
    },
    formatNumber(val) {
       if (val === undefined || val === null) return "0.0000";
       return val.toFixed(4);
    },
    loadResult() {
      this.loading = true;
      getAttackResult(this.taskId).then(response => {
        this.result = response.data;
        this.loading = false;
        this.$nextTick(() => {
          this.initCharts();
        });
      }).catch(() => {
        this.loading = false;
        this.$modal.msgError("加载结果失败");
      });
    },
    initCharts() {
      if (!this.result.metrics || this.result.metrics.length === 0) return;

      // 准确率对比图
      const accuracyChart = echarts.init(this.$refs.accuracyChart);
      const attackLabels = this.result.metrics.map(m => m.attack_type.toUpperCase());

      accuracyChart.setOption({
        title: { text: '准确率对比', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['原始准确率', '鲁棒准确率'], bottom: 0 },
        xAxis: { type: 'category', data: attackLabels },
        yAxis: { type: 'value', max: 1, axisLabel: { formatter: '{value}' } },
        series: [
          {
            name: '原始准确率',
            type: 'bar',
            data: this.result.metrics.map(m => m.clean_accuracy),
            itemStyle: { color: '#409EFF' }
          },
          {
            name: '鲁棒准确率',
            type: 'bar',
            data: this.result.metrics.map(m => m.robust_accuracy),
            itemStyle: { color: '#67C23A' }
          }
        ]
      });

      // 扰动量图
      const perturbationChart = echarts.init(this.$refs.perturbationChart);
      perturbationChart.setOption({
        title: { text: '扰动量分析', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['L2 扰动', 'L∞ 扰动', '攻击成功率'], bottom: 0 },
        xAxis: { type: 'category', data: attackLabels },
        yAxis: [
          { type: 'value', name: '扰动量', position: 'left' },
          { type: 'value', name: '成功率', position: 'right', max: 1 }
        ],
        series: [
          {
            name: 'L2 扰动',
            type: 'bar',
            data: this.result.metrics.map(m => m.avg_perturbation_l2),
            itemStyle: { color: '#E6A23C' }
          },
          {
            name: 'L∞ 扰动',
            type: 'bar',
            data: this.result.metrics.map(m => m.avg_perturbation_linf),
            itemStyle: { color: '#F56C6C' }
          },
          {
            name: '攻击成功率',
            type: 'line',
            yAxisIndex: 1,
            data: this.result.metrics.map(m => m.attack_success_rate),
            itemStyle: { color: '#909399' }
          }
        ]
      });
    },
    goBack() {
      this.$router.push("/robustness/task");
    },
    exportToPDF() {
      this.$modal.loading("正在导出PDF...");

      try {
        console.log('使用浏览器打印功能导出PDF...');

        // 获取要导出的内容
        const content = document.querySelector('.box-card');
        if (!content) {
          throw new Error('找不到要导出的内容');
        }

        // 为内容添加一个唯一ID
        const originalId = content.id;
        const contentId = 'print-content-' + Date.now();
        content.id = contentId;

        // 调整内容样式
        const originalStyle = content.style.cssText;
        content.style.width = '100%';
        content.style.backgroundColor = 'white';
        content.style.padding = '20px';
        content.style.boxSizing = 'border-box';

        // 调整图表容器高度
        const accuracyChartEl = this.$refs.accuracyChart;
        const perturbationChartEl = this.$refs.perturbationChart;

        let originalAccuracyHeight = '';
        let originalPerturbationHeight = '';
        let originalAccuracyClass = '';
        let originalPerturbationClass = '';

        if (accuracyChartEl) {
          originalAccuracyHeight = accuracyChartEl.style.height;
          originalAccuracyClass = accuracyChartEl.className;
          accuracyChartEl.style.height = '400px';
          accuracyChartEl.className += ' print-chart';
        }
        if (perturbationChartEl) {
          originalPerturbationHeight = perturbationChartEl.style.height;
          originalPerturbationClass = perturbationChartEl.className;
          perturbationChartEl.style.height = '400px';
          perturbationChartEl.className += ' print-chart';
        }

        // 重新渲染图表以适应新高度
        this.initCharts();

        // 创建打印样式
        const style = document.createElement('style');
        style.textContent = `
          @media print {
            /* 隐藏所有内容 */
            body * {
              visibility: hidden;
            }
            /* 只显示测试结果内容 */
            #${contentId}, #${contentId} * {
              visibility: visible;
            }
            /* 调整内容位置和样式 */
            #${contentId} {
              position: absolute;
              left: -50px;
              top: -10px;
              width: 120%;
              height: auto;
              min-height: 100%;
              padding: 5px;
              box-sizing: border-box;
              background-color: white;
            }
            /* 确保表格能正确显示 */
            #${contentId} table {
              width: 100%;
              border-collapse: collapse;
              font-size: 7px;
            }
            /* 确保表格列能正确显示 */
            #${contentId} th,
            #${contentId} td {
              padding: 2px;
              text-align: center;
              white-space: nowrap;
            }
            /* 确保图表容器有足够的高度 */
            #${contentId} .el-col {
              page-break-inside: avoid;
            }
            #${contentId} .el-card__header {
              display: none;
            }
            /* 确保图表容器有足够的高度 */
            #${contentId} div {
              page-break-inside: avoid;
            }
            /* 确保图表显示完整 */
            #${contentId} .print-chart {
              height: 300px !important;
              min-height: 300px;
              width: 100% !important;
            }
            /* 确保页面设置 */
            @page {
              size: landscape;
              margin: 2mm;
            }
          }
        `;
        document.head.appendChild(style);

        // 等待图表渲染
        setTimeout(() => {
          try {
            console.log('开始打印...');
            // 调用打印功能
            window.print();

            // 恢复原始状态
            if (originalId) {
              content.id = originalId;
            } else {
              content.removeAttribute('id');
            }

            content.style.cssText = originalStyle;

            if (accuracyChartEl) {
              accuracyChartEl.style.height = originalAccuracyHeight;
              accuracyChartEl.className = originalAccuracyClass;
            }
            if (perturbationChartEl) {
              perturbationChartEl.style.height = originalPerturbationHeight;
              perturbationChartEl.className = originalPerturbationClass;
            }

            // 移除打印样式
            if (document.head.contains(style)) {
              document.head.removeChild(style);
            }

            // 重新渲染图表以恢复原始状态
            this.initCharts();

            this.$modal.closeLoading();
            this.$modal.msgSuccess("PDF导出成功，请在打印对话框中选择保存为PDF");
            console.log('PDF导出成功');
          } catch (printError) {
            console.error('打印失败:', printError);
            // 恢复原始状态
            if (originalId) {
              content.id = originalId;
            } else {
              content.removeAttribute('id');
            }

            content.style.cssText = originalStyle;

            if (accuracyChartEl) {
              accuracyChartEl.style.height = originalAccuracyHeight;
              accuracyChartEl.className = originalAccuracyClass;
            }
            if (perturbationChartEl) {
              perturbationChartEl.style.height = originalPerturbationHeight;
              perturbationChartEl.className = originalPerturbationClass;
            }

            // 移除打印样式
            if (document.head.contains(style)) {
              document.head.removeChild(style);
            }

            // 重新渲染图表以恢复原始状态
            this.initCharts();

            this.$modal.closeLoading();
            this.$modal.msgError("PDF导出失败，请重试");
          }
        }, 2000); // 增加等待时间，确保图表完全渲染

      } catch (error) {
        console.error('导出失败:', error);
        this.$modal.closeLoading();
        this.$modal.msgError(`PDF导出失败: ${error.message}`);
      }
    }
  }
};
</script>

<style scoped>
.stat-box {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  transition: all 0.3s;
}
.stat-box:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}
.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.stat-value.primary { color: #409EFF; }
.stat-value.success { color: #67C23A; }
.stat-value.danger { color: #F56C6C; }
</style>
