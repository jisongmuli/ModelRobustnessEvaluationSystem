<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch">
      <el-form-item label="任务状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="全部" clearable>
          <el-option label="等待中" value="pending" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 工具栏 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleAdd"
        >新建测试</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="taskList">
      <el-table-column label="任务ID" align="center" prop="task_id" width="180" />
      <el-table-column label="模型ID" align="center" prop="model_id" width="180" />
      <el-table-column label="状态" align="center" prop="status" width="100">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" align="center" prop="progress" width="150">
        <template slot-scope="scope">
          <el-progress
            :percentage="scope.row.progress"
            :status="scope.row.status === 'completed' ? 'success' : (scope.row.status === 'failed' ? 'exception' : undefined)"
            :stroke-width="10"
          />
        </template>
      </el-table-column>
      <el-table-column label="当前攻击" align="center" prop="current_attack" width="120">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.current_attack" size="small">
            {{ scope.row.current_attack.toUpperCase() }}
          </el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="create_time" width="180">
        <template slot-scope="scope">
          {{ parseTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="结束时间" align="center" prop="end_time" width="180">
        <template slot-scope="scope">
          {{ scope.row.end_time ? parseTime(scope.row.end_time) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="180">
        <template slot-scope="scope">
          <el-button
            v-if="scope.row.status === 'completed'"
            size="mini"
            type="text"
            icon="el-icon-view"
            @click="handleView(scope.row)"
          >查看结果</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="queryParams.page"
      :limit.sync="queryParams.page_size"
      @pagination="getList"
    />
  </div>
</template>

<script>
import { getAttackTaskList, deleteAttackTask } from "@/api/robustness/attack";

export default {
  name: "TaskList",
  data() {
    return {
      loading: true,
      showSearch: true,
      total: 0,
      taskList: [],
      queryParams: {
        page: 1,
        page_size: 10,
        status: undefined
      },
      pollTimer: null
    };
  },
  created() {
    this.getList();
    this.startPolling();
  },
  activated() {
    this.getList();
    this.startPolling();
  },
  deactivated() {
    clearInterval(this.pollTimer);
    this.pollTimer = null;
  },
  beforeDestroy() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
    }
  },
  methods: {
    /** 查询任务列表 */
    getList() {
      this.loading = true;
      getAttackTaskList(this.queryParams).then(response => {
        this.taskList = response.data;
        this.total = response.total;
        this.loading = false;
      }).catch(() => {
        this.loading = false;
      });
    },
    /** 自动刷新列表 */
    startPolling() {
      clearInterval(this.pollTimer);
      this.pollTimer = setInterval(() => {
        // 如果有运行中的任务，自动刷新
        const hasRunning = this.taskList.some(t => t.status === 'running' || t.status === 'pending');
        if (hasRunning) {
          this.getList();
        }
      }, 5000);
    },
    handleQuery() {
      this.queryParams.page = 1;
      this.getList();
    },
    resetQuery() {
      this.resetForm("queryForm");
      this.handleQuery();
    },
    handleAdd() {
      this.$router.push("/robustness/attack");
    },
    handleView(row) {
      this.$router.push({ path: `/robustness/result/${row.task_id}` });
    },
    handleDelete(row) {
      this.$modal.confirm('是否确认删除该任务？').then(() => {
        return deleteAttackTask(row.task_id);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    getStatusType(status) {
      const types = {
        pending: "info",
        running: "warning",
        completed: "success",
        failed: "danger"
      };
      return types[status] || "info";
    },
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
