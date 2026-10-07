<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>对抗攻击测试</span>
      </div>

      <el-form ref="form" :model="form" :rules="rules" label-width="120px">
        <!-- 选择模型 -->
        <el-form-item label="选择模型" prop="model_id">
          <el-select v-model="form.model_id" placeholder="请选择要测试的模型" style="width: 100%">
            <el-option
              v-for="item in modelList"
              :key="item.id"
              :label="`${item.filename} (${item.model_type || '未知类型'})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <!-- 测试数据集 -->
        <el-form-item label="测试数据">
          <el-radio-group v-model="form.datasetType">
            <el-radio label="cifar10">默认 (CIFAR-10)</el-radio>
            <el-radio label="custom">自定义数据集</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="form.datasetType === 'custom'" label="选择数据集" prop="dataset_id">
          <el-row :gutter="10">
            <el-col :span="18">
              <el-select v-model="form.dataset_id" placeholder="请选择数据集" style="width: 100%">
                <el-option
                  v-for="item in datasetList"
                  :key="item.id"
                  :label="`${item.name} (${item.num_classes}类)`"
                  :value="item.id"
                />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-upload
                action="#"
                :http-request="handleUploadDataset"
                :show-file-list="false"
              >
                <el-button size="small" type="primary" :loading="uploading">上传新数据</el-button>
              </el-upload>
            </el-col>
          </el-row>
          <div class="form-tip">支持 .zip 格式，解压后需为 ImageFolder 结构 (root/class/image.jpg)</div>
          <div v-if="selectedDataset" class="form-tip">
            数据集共有 {{ selectedDataset.num_images }} 张图像；标签顺序：
            {{ (selectedDataset.classes || []).map((name, index) => `${index}: ${name}`).join('，') }}
          </div>
        </el-form-item>

        <!-- 攻击类型选择 -->
        <el-form-item label="模型预处理">
          <el-select v-model="form.normalization">
            <el-option label="默认：CIFAR-10 / 自定义数据 ImageNet" value="auto" />
            <el-option label="不标准化（模型内部已处理）" value="none" />
            <el-option label="CIFAR-10 均值与标准差" value="cifar10" />
            <el-option label="ImageNet 均值与标准差" value="imagenet" />
          </el-select>
          <div class="form-tip">请选择训练模型时使用的预处理；扰动强度按 0–1 像素范围计算。</div>
        </el-form-item>
        <el-form-item label="随机种子">
          <el-input-number v-model="form.seed" :min="0" :max="2147483647" />
        </el-form-item>
        <el-form-item label="攻击类型" prop="attacks">
          <el-checkbox-group v-model="selectedAttacks">
            <el-checkbox
              v-for="attack in attackTypes"
              :key="attack.type"
              :label="attack.type"
            >
              {{ attack.name }}
              <el-tooltip :content="attack.description" placement="top">
                <i class="el-icon-question"></i>
              </el-tooltip>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 攻击参数配置 -->
        <el-divider content-position="left">攻击参数配置</el-divider>

        <el-form-item label="扰动强度 (ε)">
          <el-slider
            v-model="form.eps"
            :min="0.001"
            :max="0.1"
            :step="0.001"
            :format-tooltip="val => val ? val.toFixed(3) : val"
            show-input
          />
        </el-form-item>

        <el-form-item label="迭代步数">
          <el-input-number v-model="form.steps" :min="1" :max="100" />
          <span class="form-tip">适用于 PGD、BIM 等迭代攻击</span>
        </el-form-item>

        <el-form-item label="测试样本数">
          <el-input-number v-model="form.num_samples" :min="1" :max="10000" :step="100" />
        </el-form-item>

        <el-form-item label="批次大小">
          <el-input-number v-model="form.batch_size" :min="1" :max="128" />
        </el-form-item>

        <!-- 提交按钮 -->
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            {{ submitting ? '测试中...' : '开始测试' }}
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 测试进度 -->
    <el-card v-if="currentTask" class="box-card" style="margin-top: 20px;">
      <div slot="header" class="clearfix">
        <span>测试进度</span>
        <el-tag :type="getStatusType(currentTask.status)" style="float: right;">
          {{ getStatusText(currentTask.status) }}
        </el-tag>
      </div>

      <el-progress
        :percentage="currentTask.progress"
        :status="currentTask.status === 'completed' ? 'success' : (currentTask.status === 'failed' ? 'exception' : undefined)"
      />

      <p v-if="currentTask.current_attack" style="margin-top: 10px;">
        当前攻击: <el-tag size="small">{{ currentTask.current_attack.toUpperCase() }}</el-tag>
      </p>

      <el-button
        v-if="currentTask.status === 'completed'"
        type="primary"
        size="small"
        style="margin-top: 10px;"
        @click="viewResult"
      >
        查看结果
      </el-button>
    </el-card>
  </div>
</template>

<script>
import { listModel } from "@/api/robustness/model";
import { getSupportedAttacks, startAttack, getAttackStatus } from "@/api/robustness/attack";
import { listDataset, uploadDataset } from "@/api/robustness/dataset";

export default {
  name: "AttackTest",
  data() {
    return {
      // 模型列表
      modelList: [],
      // 数据集列表
      datasetList: [],
      // 攻击类型
      attackTypes: [],
      // 选中的攻击
      selectedAttacks: ["fgsm", "pgd"],
      // 表单数据
      form: {
        model_id: "",
        datasetType: "cifar10", // cifar10 or custom
        dataset_id: "",
        eps: 0.03,
        steps: 10,
        num_samples: 200,
        batch_size: 32,
        normalization: "auto",
        seed: 42
      },
      // 验证规则
      rules: {
        model_id: [{ required: true, message: "请选择模型", trigger: "change" }]
      },
      // 提交状态
      submitting: false,
      uploading: false,
      // 当前任务
      currentTask: null,
      // 轮询定时器
      pollTimer: null
    };
  },
  computed: {
    selectedDataset() {
      return this.datasetList.find(item => item.id === this.form.dataset_id);
    }
  },
  created() {
    this.loadModels();
    this.loadDatasets();
    this.loadAttackTypes();

    // 如果有传入 modelId，自动选中
    if (this.$route.query.modelId) {
      this.form.model_id = this.$route.query.modelId;
    }
  },
  activated() {
    // Cached tabs must see models/datasets uploaded since the first visit.
    this.loadModels();
    this.loadDatasets();
    if (this.$route.query.modelId) this.form.model_id = this.$route.query.modelId;
  },
  watch: {
    '$route.query.modelId'(value) {
      if (value && this.$route.path === '/robustness/attack') this.form.model_id = value;
    }
  },
  beforeDestroy() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
    }
  },
  methods: {
    /** 加载模型列表 */
    loadModels() {
      listModel().then(response => {
        this.modelList = response.data;
      });
    },
    /** 加载数据集列表 */
    loadDatasets() {
      listDataset().then(response => {
        this.datasetList = response.data || [];
      });
    },
    /** 加载攻击类型 */
    loadAttackTypes() {
      getSupportedAttacks().then(response => {
        this.attackTypes = response.data;
      });
    },
    /** 自定义数据集上传 */
    handleUploadDataset(param) {
      this.uploading = true;
      const formData = new FormData();
      formData.append("file", param.file);

      uploadDataset(formData).then(response => {
        this.$modal.msgSuccess("数据集上传成功");
        this.loadDatasets();
        this.form.datasetType = "custom";
        this.form.dataset_id = response.data.id;
        this.uploading = false;
      }).catch(() => {
        this.$modal.msgError("上传失败");
        this.uploading = false;
      });
    },
    /** 提交表单 */
    submitForm() {
      this.$refs.form.validate(valid => {
        if (!valid) return;

        if (this.selectedAttacks.length === 0) {
          this.$modal.msgError("请至少选择一种攻击类型");
          return;
        }

        if (this.form.datasetType === 'custom' && !this.form.dataset_id) {
            this.$modal.msgError("请选择自定义数据集");
            return;
        }

        this.submitting = true;

        const attacks = this.selectedAttacks.map(type => ({
          attack_type: type,
          eps: this.form.eps,
          steps: this.form.steps
        }));

        startAttack({
          model_id: this.form.model_id,
          dataset_id: this.form.datasetType === 'custom' ? this.form.dataset_id : null,
          attacks: attacks,
          batch_size: this.form.batch_size,
          num_samples: this.form.num_samples,
          normalization: this.form.normalization,
          seed: this.form.seed
        }).then(response => {
          this.currentTask = response.data;
          this.$modal.msgSuccess("任务已创建");
          this.startPolling();
        }).catch(() => {
          this.submitting = false;
        });
      });
    },
    /** 开始轮询任务状态 */
    startPolling() {
      if (this.pollTimer) clearInterval(this.pollTimer);
      this.pollTimer = setInterval(() => {
        getAttackStatus(this.currentTask.task_id).then(response => {
          this.currentTask = response.data;

          if (this.currentTask.status === "completed" || this.currentTask.status === "failed") {
            clearInterval(this.pollTimer);
            this.submitting = false;

            if (this.currentTask.status === "completed") {
              this.$modal.msgSuccess("测试完成");
            } else {
              this.$modal.msgError("测试失败: " + this.currentTask.error_msg);
            }
          }
        }).catch(() => {
          clearInterval(this.pollTimer);
          this.pollTimer = null;
          this.submitting = false;
          this.$modal.msgError("无法查询任务状态，请在任务列表中重试查询");
        });
      }, 2000);
    },
    /** 查看结果 */
    viewResult() {
      this.$router.push({ path: `/robustness/result/${this.currentTask.task_id}` });
    },
    /** 重置表单 */
    resetForm() {
      this.$refs.form.resetFields();
      this.selectedAttacks = ["fgsm", "pgd"];
      this.form.datasetType = "cifar10";
      this.form.dataset_id = "";
      this.form.normalization = "auto";
      this.form.seed = 42;
    },
    /** 获取状态类型 */
    getStatusType(status) {
      const types = {
        pending: "info",
        running: "warning",
        completed: "success",
        failed: "danger"
      };
      return types[status] || "info";
    },
    /** 获取状态文本 */
    getStatusText(status) {
      const texts = {
        pending: "等待中",
        running: "运行中",
        completed: "已完成",
        failed: "失败"
      };
      return texts[status] || status;
    }
  }
};
</script>

<style scoped>
.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>
