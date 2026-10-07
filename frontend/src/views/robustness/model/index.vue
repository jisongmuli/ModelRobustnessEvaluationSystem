<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="模型名称" prop="filename">
        <el-input
          v-model="queryParams.filename"
          placeholder="请输入模型名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleUpload"
        >上传模型</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
        >删除</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="modelList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="模型ID" align="center" prop="id" width="180" />
      <el-table-column label="文件名" align="center" prop="filename" :show-overflow-tooltip="true" />
      <el-table-column label="模型类型" align="center" prop="model_type" width="140">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.model_type" type="success">{{ scope.row.model_type }}</el-tag>
          <el-tag v-else type="info">未识别</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="类别数" align="center" prop="num_classes" width="100" />
      <el-table-column label="输入尺寸" align="center" prop="img_size" width="100">
        <template slot-scope="scope">
          {{ scope.row.img_size || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="文件大小" align="center" prop="file_size" width="120">
        <template slot-scope="scope">
          {{ formatFileSize(scope.row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column label="上传时间" align="center" prop="upload_time" width="180">
        <template slot-scope="scope">
          {{ parseTime(scope.row.upload_time) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status" width="170">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
          <el-tooltip v-if="scope.row.load_error" :content="scope.row.load_error" placement="top">
            <i class="el-icon-warning-outline warning-icon"></i>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="260">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-setting"
            @click="handleConfig(scope.row)"
          >配置</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-video-play"
            @click="handleTest(scope.row)"
          >测试</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="queryParams.page"
      :limit.sync="queryParams.page_size"
      @pagination="getList"
    />

    <el-dialog title="上传模型" :visible.sync="uploadOpen" width="500px" append-to-body>
      <el-upload
        ref="upload"
        drag
        :action="uploadUrl"
        :headers="headers"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        accept=".pt,.pth"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将模型文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">
          只能上传 .pt 或 .pth 格式的 PyTorch 模型文件，大小不超过 500MB
        </div>
      </el-upload>
    </el-dialog>

    <el-dialog title="配置模型参数" :visible.sync="configOpen" width="520px" append-to-body>
      <el-form ref="configForm" :model="configForm" :rules="configRules" label-width="110px">
        <el-form-item label="模型类型" prop="model_type">
          <el-select
            v-model="configForm.model_type"
            filterable
            allow-create
            default-first-option
            placeholder="请选择或输入模型类型"
            style="width: 100%"
          >
            <el-option v-for="item in modelTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="类别数" prop="num_classes">
          <el-input-number v-model="configForm.num_classes" :min="1" :max="100000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="输入尺寸" prop="img_size">
          <el-input-number v-model="configForm.img_size" :min="16" :max="2048" style="width: 100%" />
        </el-form-item>
        <el-form-item label="分类头名称" prop="head_name">
          <el-select v-model="configForm.head_name" clearable placeholder="默认按模型类型推断" style="width: 100%">
            <el-option label="fc" value="fc" />
            <el-option label="classifier" value="classifier" />
            <el-option label="head" value="head" />
          </el-select>
        </el-form-item>
        <div class="config-tip">
          常见组合：ResNet 用 <code>fc</code>，EfficientNet/MobileNet/VGG/DenseNet 常用 <code>classifier</code>。
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="configOpen = false">取 消</el-button>
        <el-button type="primary" :loading="configLoading" @click="submitConfig">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { configureModel, delModel, getModelConfig, listModel } from "@/api/robustness/model";
import { getToken } from "@/utils/auth";

export default {
  name: "ModelManage",
  data() {
    return {
      loading: true,
      ids: [],
      multiple: true,
      showSearch: true,
      total: 0,
      modelList: [],
      queryParams: {
        page: 1,
        page_size: 10,
        filename: undefined
      },
      uploadOpen: false,
      configOpen: false,
      configLoading: false,
      uploadUrl: process.env.VUE_APP_BASE_API + "/api/model/upload",
      headers: {
        Authorization: "Bearer " + getToken()
      },
      modelTypeOptions: [
        "resnet18",
        "resnet34",
        "resnet50",
        "resnet101",
        "vgg16",
        "vgg19",
        "efficientnet_b0",
        "efficientnet_b1",
        "mobilenet_v2",
        "mobilenet_v3_small",
        "densenet121"
      ],
      configForm: {
        model_id: "",
        model_type: "",
        num_classes: 10,
        img_size: 224,
        head_name: "",
        has_custom_fc: false
      },
      configRules: {
        model_type: [{ required: true, message: "请输入模型类型", trigger: "change" }],
        num_classes: [{ required: true, message: "请输入类别数", trigger: "blur" }],
        img_size: [{ required: true, message: "请输入输入尺寸", trigger: "blur" }]
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      this.loading = true;
      listModel(this.queryParams).then(response => {
        this.modelList = response.data;
        this.total = response.total;
        this.loading = false;
      }).catch(() => {
        this.loading = false;
      });
    },
    handleQuery() {
      this.queryParams.page = 1;
      this.getList();
    },
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.id);
      this.multiple = !selection.length;
    },
    handleUpload() {
      this.uploadOpen = true;
    },
    handleUploadSuccess(response) {
      if (response.code === 200) {
        if (response.data && response.data.status === "needs_config") {
          this.$modal.msgWarning(response.msg || "上传成功，但需要补充模型参数");
        } else {
          this.$modal.msgSuccess(response.msg || "上传成功");
        }
        this.uploadOpen = false;
        this.getList();
      } else {
        this.$modal.msgError(response.msg || "上传失败");
      }
    },
    handleUploadError() {
      this.$modal.msgError("上传失败");
    },
    beforeUpload(file) {
      const isValidType = file.name.endsWith('.pt') || file.name.endsWith('.pth');
      const isLt500M = file.size / 1024 / 1024 < 500;

      if (!isValidType) {
        this.$modal.msgError("只能上传 .pt 或 .pth 格式的文件");
        return false;
      }
      if (!isLt500M) {
        this.$modal.msgError("文件大小不能超过 500MB");
        return false;
      }
      return true;
    },
    handleConfig(row) {
      const fallbackModelType = row.model_type || "resnet18";
      const fallbackHeadName = this.getDefaultHeadName(fallbackModelType);
      this.configForm = {
        model_id: row.id,
        model_type: fallbackModelType,
        num_classes: row.num_classes || 10,
        img_size: row.img_size || 224,
        head_name: fallbackHeadName,
        has_custom_fc: false
      };
      getModelConfig(row.id).then(response => {
        if (response.data) {
          this.configForm = {
            ...this.configForm,
            ...response.data,
            head_name: response.data.head_name || this.getDefaultHeadName(response.data.model_type || fallbackModelType)
          };
        }
      }).finally(() => {
        this.configOpen = true;
      });
    },
    submitConfig() {
      this.$refs.configForm.validate(valid => {
        if (!valid) {
          return;
        }
        this.configLoading = true;
        configureModel(this.configForm).then(response => {
          this.$modal.msgSuccess(response.msg || "配置成功");
          this.configOpen = false;
          this.getList();
        }).finally(() => {
          this.configLoading = false;
        });
      });
    },
    handleTest(row) {
      this.$router.push({ path: "/robustness/attack", query: { modelId: row.id } });
    },
    handleDelete(row) {
      const modelIds = row.id ? [row.id] : this.ids;
      this.$modal.confirm('是否确认删除选中的模型？').then(() => {
        const promises = modelIds.map(id => delModel(id));
        return Promise.all(promises);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    formatFileSize(bytes) {
      if (!bytes) return "0 B";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return (bytes / Math.pow(k, i)).toFixed(2) + " " + sizes[i];
    },
    getStatusType(status) {
      const map = {
        ready: "success",
        needs_config: "warning"
      };
      return map[status] || "info";
    },
    getStatusText(status) {
      const map = {
        ready: "就绪",
        needs_config: "待配置"
      };
      return map[status] || status;
    },
    getDefaultHeadName(modelType) {
      const classifierModels = ["vgg16", "vgg19", "efficientnet_b0", "efficientnet_b1", "mobilenet_v2", "mobilenet_v3_small", "densenet121"];
      return classifierModels.includes(modelType) ? "classifier" : "fc";
    }
  }
};
</script>

<style scoped>
.warning-icon {
  margin-left: 6px;
  color: #e6a23c;
  cursor: pointer;
}

.config-tip {
  margin-left: 110px;
  color: #909399;
  font-size: 12px;
  line-height: 1.6;
}
</style>
