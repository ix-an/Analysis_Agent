<script>
export default {
  name: "Login",
  data() {  // 数据
    return {
      email: "",  // 邮箱
      code: "",   // 验证码
      activeTab: "login" // 当前激活的标签页：login-登录，register-注册
    };
  },
  methods: {  // 方法
    // 发送登录验证码
    sendLoginCode() {
      if (!this.email) {
        this.$message.warning("请先输入邮箱！");
        return;
      }
      const p = { "email": this.email };
      // 发送 AJAX 请求
      this.$http.post("http://localhost:8000/send_code", p)
        .then(res => {
          if (res.data.code === 200) {
            this.$message.success(res.data.msg);
            this.code = "";  // 清空验证码输入框
          } else {
            this.$message.warning(res.data.msg);
          }
        })
        .catch(err => {
          this.$message.error("请求失败，请稍后重试");
          console.error("发送登录验证码失败：", err);
        });
    },

    // 发送注册验证码
    sendRegisterCode() {
      if (!this.email) {
        this.$message.warning("请先输入邮箱！");
        return;
      }
      const p = { "email": this.email };
      // 发送 AJAX 请求
      this.$http.post("http://localhost:8000/send_register_code", p)
        .then(res => {
          if (res.data.code === 200) {
            this.$message.success(res.data.msg);
            this.code = "";  // 清空验证码输入框
          } else {
            this.$message.warning(res.data.msg);
          }
        })
        .catch(err => {
          this.$message.error("请求失败，请稍后重试");
          console.error("发送注册验证码失败：", err);
        });
    },

    // 登录
    login() {
      if (!this.email || !this.code) {
        this.$message.warning("邮箱和验证码不能为空！");
        return;
      }
      // 定义登录接口参数
      const p = {
        "email": this.email,
        "code": this.code
      };
      // 发送 AJAX 请求
      this.$http.post("http://localhost:8000/login", p)
        .then(res => {
          if (res.data.code === 200) {
            this.$message.success(res.data.msg);
            this.$router.push({ name: "Chat" });
            // 把用户邮箱作为ID 保存到本地存储中
            localStorage.setItem("userId", this.email);
          } else {
            this.$message.warning(res.data.msg);
          }
        })
        .catch(err => {
          this.$message.error("登录请求失败，请稍后重试");
          console.error("登录失败：", err);
        });
    },

    // 注册
    register() {
      if (!this.email || !this.code) {
        this.$message.warning("邮箱和验证码不能为空！");
        return;
      }
      // 定义注册接口参数
      const p = {
        "email": this.email,
        "code": this.code
      };
      // 发送 AJAX 请求
      this.$http.post("http://localhost:8000/register", p)
        .then(res => {
          if (res.data.code === 200) {
            this.$message.success(res.data.msg);
            // 注册成功后切换到登录标签页
            this.activeTab = "login";
            this.email = "";
            this.code = "";
          } else {
            this.$message.warning(res.data.msg);
          }
        })
        .catch(err => {
          this.$message.error("注册请求失败，请稍后重试");
          console.error("注册失败：", err);
        });
    },

    // 统一的发送验证码入口（根据当前标签页调用对应方法）
    sendCode() {
      if (this.activeTab === "login") {
        this.sendLoginCode();
      } else {
        this.sendRegisterCode();
      }
    }
  }
};
</script>

<template>
  <div class="login-one">
    <div class="login-container">

      <!-- 标题 -->
      <div class="title">
        <h1>☁️ AI智能数据分析助手 ☁️</h1>
        <p>轻松分析 · 简洁交互 · 高效输出</p>
      </div>

      <!-- 卡片 -->
      <div class="login-card">
        <el-tabs v-model="activeTab">
          <!-- 登录标签页 -->
          <el-tab-pane label="🌷 登录" name="login">
            <el-form label-width="70px">
              <el-form-item label="邮箱">
                <el-input
                  v-model="email"
                  placeholder="请输入邮箱 📮"
                  type="email"
                ></el-input>
              </el-form-item>

              <el-form-item label="验证码">
                <div class="code-row">
                  <el-input
                    v-model="code"
                    placeholder="输入验证码 ✉️"
                    maxlength="4"
                  ></el-input>
                  <el-button
                    class="code-btn"
                    @click="sendLoginCode"
                    type="primary"
                  >发送</el-button>
                </div>
              </el-form-item>

              <el-form-item>
                <el-button
                  class="main-btn"
                  @click="login"
                  type="primary"
                >登录</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 注册标签页 -->
          <el-tab-pane label="🍓 注册" name="register">
            <el-form label-width="70px">
              <el-form-item label="邮箱">
                <el-input
                  v-model="email"
                  placeholder="请输入邮箱 📮"
                  type="email"
                ></el-input>
              </el-form-item>

              <el-form-item label="验证码">
                <div class="code-row">
                  <el-input
                    v-model="code"
                    placeholder="输入验证码 ✉️"
                    maxlength="4"
                  ></el-input>
                  <el-button
                    class="code-btn"
                    @click="sendRegisterCode"
                    type="primary"
                  >发送</el-button>
                </div>
              </el-form-item>

              <el-form-item>
                <el-button
                  class="main-btn"
                  @click="register"
                  type="primary"
                >注册</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 整体背景 */
.login-one {
  height: 100vh;
  background: linear-gradient(135deg, #fef6f6, #f6fbff);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  padding: 0;
}

/* 容器 */
.login-container {
  width: 420px;
}

/* 标题 */
.title {
  text-align: center;
  margin-bottom: 20px;
}

.title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #444;
  margin: 0;
}

.title p {
  font-size: 13px;
  color: #999;
  margin-top: 6px;
}

/* 卡片 */
.login-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 25px 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

/* 输入框柔化 */
.el-input__inner {
  border-radius: 10px;
  background-color: #fafafa;
  border: 1px solid #e8e8e8;
}

/* 验证码行 */
.code-row {
  display: flex;
  gap: 10px;
}

.code-btn {
  border-radius: 10px;
  background-color: #ffe4e1 !important;
  color: #ff7a7a !important;
  border: none !important;
  flex-shrink: 0;
  width: 100px;
}

.code-btn:hover {
  background-color: #ffd6d1 !important;
}

/* 主按钮 */
.main-btn {
  width: 100%;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffd1dc, #cde7ff) !important;
  border: none !important;
  color: #555 !important;
  font-weight: 500;
  height: 40px;
}

.main-btn:hover {
  opacity: 0.9;
}

/* tabs优化 */
::v-deep(.el-tabs__item) {
  color: #888;
  font-size: 14px;
}

::v-deep(.el-tabs__item.is-active) {
  color: #ff8fa3;
  font-weight: 500;
}

::v-deep(.el-tabs__active-bar) {
  background-color: #ffb6c1;
}

::v-deep(.el-tabs__header) {
  margin-bottom: 20px;
}
</style>
