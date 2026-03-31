<script>
import {marked} from 'marked'
import DOMPurify from 'dompurify'
import * as echarts from 'echarts';

export default {
  name: "Chat",
  data() {
    return {
      thinking: false, // 是否正在思考
      userId: "", // 用户id
      isChat: false,//是否点击了新对话
      inputMessage: "发消息...", //输入的消息
      userAvatar: require('@/assets/image/user.jpeg'), // 用户头像
      botAvatar: require('@/assets/image/bot.jpeg'),  // 机器人头像
      activeChatId: "1",// 当前聊天id
      chatList: [],// 历史聊天列表
      isShow: false, //是否显示数据分析页面

    }
  },
  computed: {//计算属性
    currentChat() {
      return this.chatList.find(x => x.id === this.activeChatId) || {"messages": []};
    }
  },
  mounted() {// 初始化生命周期函数
    // 获取本地存储的用户id，赋值给userId
    this.userId = localStorage.getItem("userId");


  },
  methods: {
    uploadSuccess(response) {//文件上传
      if (response.code === 200) {
        //定义输入内容
        this.inputMessage = "分析这个文件的内容并生成报告:"+response.filename;
        //发送信息
        this.sendMessage();

      } else {
        this.$message.error("上传失败");
      }

    },
    selectChat(id) {
      this.activeChatId = id;
    },
    newChat() { //新建对话
      //定义新的对话
      //用当前时间作为消息id
      const id = new Date().getTime().toString();
      const chat = {"id": id, "title": "新对话", "messages": []};
      this.chatList.push(chat);
      //选中对话
      this.activeChatId = id;
      this.isChat = true;

    },

    formatMessage(content) { // 格式化消息
      // 使用marked解析markdown并净化HTML
      return DOMPurify.sanitize(marked.parse(content || ''))
    },
    showEcharts(data) {

      //用当前时间作为消息id
      const id = new Date().getTime().toString();
      const reply = {"id": id, role: "assistant", content: "", type: "chart"};
      // 添加回复消息
      this.currentChat.messages.push(reply);
      this.$forceUpdate();
      //初始化图表
      this.$nextTick(() => {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart-' + id));

        //把字符串类型转换成json类型
        const json = JSON.parse(data);
        // 绘制图表
        myChart.setOption(json);
      });
    },
    showAnalyze(data) { //显示数据分析结果


      //用当前时间作为消息id
      const id = new Date().getTime().toString();
      const reply = {"id": id, role: "assistant", content: data, type: "anlyze"};
      // 添加回复消息
      this.currentChat.messages.push(reply);
      this.$forceUpdate();
      //初始化图表
      this.$nextTick(() => {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById('chart-' + id));
        //把字符串类型转换成json类型
        const json = JSON.parse(data.json);
        // 绘制图表
        myChart.setOption(json);
      });

    },

    sendMessage() {// 发送消息
      // 根据用户问题判断响应处理结果
      if (this.inputMessage.indexOf("图表") > -1) {
        //显示思考
        this.thinking = true;
        //消息id,唯一性
        const id = new Date().getTime().toString();
        //添加用户的消息格式
        const roleMessage = {"id": id, "role": "user", "content": this.inputMessage, "type": "text"}
        //添加用户的消息格式
        this.currentChat.messages.push(roleMessage);
               this.$forceUpdate();
            //定义发送消息的参数
            const p = {"question":this.inputMessage,"user_id":this.userId};
            //发送ajax请求
            this.$http.get("http://localhost:8000/chat",{params:p})
              .then(rs=> {
                  //关闭思考提示
                  this.thinking = false;
                 if (rs.data.code === 200){
                      //显示图表
                      this.showEcharts(rs.data.json)
                 }else{
                   this.$message.error(rs.data.msg);
                 }
              })
      } else if (this.inputMessage.indexOf("数据分析") > -1) {
        //显示思考
        this.thinking = true;
        //消息id,唯一性
        const id = new Date().getTime().toString();
        //添加用户的消息格式
        const roleMessage = {"id": id, "role": "user", "content": this.inputMessage, "type": "text"}
        //添加用户的消息格式
        this.currentChat.messages.push(roleMessage);
        this.$forceUpdate();
        //定义发送消息的参数
        const p = {"question": this.inputMessage, "user_id": this.userId};
        //发送ajax请求
        this.$http.get("http://localhost:8000/chat", {params: p})
          .then(rs => {
            //关闭思考提示
            this.thinking = false;
            //显示数据分析结果页面
            this.isShow = true
            if (rs.data.code === 200) {
              //处理分析
              this.showAnalyze(rs.data.data);
            } else {
              this.$message.error(rs.data.msg);
            }
          })
      }
      else {
              //消息id,唯一性
      const id = new Date().getTime().toString();
      //添加用户的消息格式
      const roleMessage = {"id": id, "role": "user", "content": this.inputMessage, "type": "text"}
      //添加用户的消息格式
      this.currentChat.messages.push(roleMessage);
      //添加机器人的消息格式
      const aiMessage = {"id": id, "role": "assistant", "content": "", "type": "text"}
      this.currentChat.messages.push(aiMessage);
        //定义发送消息的参数
        const p = `question=${encodeURIComponent(this.inputMessage)}&&user_id=` + this.userId;
        //创建SSE流的链接
        const s = new EventSource("http://localhost:8000/chat?" + p);
        //处理流式消息
        s.onmessage = (e) => {
          //把流式消息转换成json对象
          const data = JSON.parse(e.data);

          //判断流式输出是否结束
          if (data.done) {
            if (data.error) { //出现异常
              //把异常信息机器人回复中
              aiMessage.content = data.content;
              //刷新视图
              this.$forceUpdate();

            }
            //关闭流
            s.close();
            return
          }
          //处理流式消息
          aiMessage.content += data.content;
          //刷新视图
          this.$forceUpdate();
        }
      }

    }

  }
}
</script>

<template>
  <el-container class="cream-container">
    <el-header class="cream-header">
      <el-row align="middle">
        <el-col :span="8">
          <h1 class="header-title">🍰 AI智能数据分析助手</h1>
        </el-col>
        <el-col :span="8">&nbsp;</el-col>
        <el-col :span="8" align="right">
          <el-button class="cream-btn" type="text">退出登录</el-button>
          <el-button class="cream-btn" type="text">用户: {{ userId }} 🧸</el-button>
        </el-col>
      </el-row>
    </el-header>
    <el-container>
      <el-aside width="260px" class="cream-aside">
        <div align="center" class="aside-top">
          <el-button class="cream-new-btn" icon="el-icon-plus" @click="newChat">新对话</el-button>
        </div>
        <hr class="cream-hr">
        <el-menu :default-active="activeChatId" @select="selectChat" class="cream-menu">
          <el-menu-item
            v-for="chat in chatList"
            :key="chat.id"
            :index="chat.id"
            class="cream-menu-item"
          >
            <i class="el-icon-chat-line-round"></i>
            <span slot="title">
                {{ chat.title.substring(0, 5) }}
                 <el-button type="text" icon="el-icon-delete" class="del-btn"></el-button>
              </span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-main class="cream-main">
          <div v-for="x in currentChat.messages" class="chat-message" :class="x.role">
            <div>
              <el-avatar class="cream-avatar" :src="x.role === 'user' ? userAvatar : botAvatar "></el-avatar>
            </div>
            <div>
              <div v-if="x.type === 'text'  " v-html="formatMessage(x.content)" class="bubble"></div>

              <div v-if="x.type === 'chart' && x.role === 'assistant' " :id="`chart-${x.id}`"
                   style="width: 800px;height: 300px" class="bubble chart-bubble"></div>

              <div v-if="isShow &&  x.content">
                  <div v-if="x.content.table" id="first">
                        <el-table :data="x.content.table.data || []" style="width: 100%">
                            <el-table-column
                              v-for=" j in x.content.table.column_name || []"
                              :label="j"
                              :prop="j"
                            ></el-table-column>
                        </el-table>
                  </div>
                  <div id="second" v-if =x.content.result v-html="formatMessage(x.content.result)" ></div>
                     <div v-if="x.content.json" :id="`chart-${x.id}`" style="width: 800px;height: 300px" class="bubble"></div>
              </div>

            </div>
          </div>
           <!-- AI思考提示 -->
            <div v-if="thinking" class="chat-message assistant">
              <div class="avatar-wrap">
                <el-avatar :src="botAvatar"></el-avatar>
              </div>
              <div class="bubble-wrap">
                <div class="bubble typing-indicator">
                  正在思考...
                </div>
              </div>
            </div>
        </el-main>
        <el-footer class="cream-footer">
          <!-- 仅修改：去掉 inline 行内布局 -->
          <el-form class="input-form">
            <!-- 仅修改：给输入框添加class，用于弹性布局 -->
            <el-form-item class="input-item">
              <el-input type="textarea" v-model="inputMessage" class="cream-input"></el-input>
            </el-form-item>

            <!-- 文件上传 -->
            <el-form-item>
              <el-upload
                action="http://localhost:8000/upload"
                :show-file-list="false"
                :on-success="uploadSuccess"
              >
                <el-button icon="el-icon-upload2">上传文件</el-button>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button class="send-btn" icon="el-icon-message" @click="sendMessage">发送</el-button>
            </el-form-item>
          </el-form>
        </el-footer>
      </el-container>
    </el-container>
  </el-container>
</template>

<style scoped>
/* ===== 日系奶油风 全局基底 ===== */
html, body, #app {
  height: 100%;
  margin: 0;
  background: linear-gradient(135deg, #fff9f9, #f0f9ff);
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 容器撑满屏幕 */
.cream-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.cream-container > .el-container {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

/* ===== 头部 奶油风 ===== */
.cream-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 18px 30px;
  border-bottom: 1px solid #fde2e4;
}

.header-title {
  font-size: 20px;
  color: #8a7d7f;
  font-weight: 500;
  margin: 0;
}

/* 头部按钮 */
.cream-btn {
  color: #a89a9d !important;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.3s;
}

.cream-btn:hover {
  background: #fde2e4 !important;
  color: #d48892 !important;
}

/* ===== 左侧边栏 ===== */
.cream-aside {
  background: #fffcfc;
  border-radius: 24px;
  margin: 12px;
  padding: 16px 0;
  box-shadow: 0 4px 12px rgba(245, 224, 227, 0.2);
}

.aside-top {
  padding: 8px 0;
}

/* 新对话按钮 */
.cream-new-btn {
  border-radius: 20px;
  background: linear-gradient(135deg, #fddde6, #d1f2ff);
  border: none;
  color: #8a7d7f;
  padding: 8px 20px;
  font-weight: 500;
  transition: all 0.3s;
}

.cream-new-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(253, 221, 230, 0.4);
}

/* 分割线 */
.cream-hr {
  border: none;
  height: 1px;
  background: #f5e1e4;
  margin: 16px 20px;
}

/* 菜单样式 */
.cream-menu {
  border: none !important;
  background: transparent !important;
}

.cream-menu-item {
  border-radius: 16px;
  margin: 6px 12px;
  color: #9d8e90;
  transition: all 0.3s;
}

.cream-menu-item:hover {
  background: #f8f1f3 !important;
  color: #d48892;
}

::v-deep(.el-menu-item.is-active) {
  background: #fddde6 !important;
  color: #d48892 !important;
  font-weight: 500;
}

.del-btn {
  color: #e4c0c5 !important;
  font-size: 12px;
}

/* ===== 聊天主区域 ===== */
.cream-main {
  background: transparent;
  padding: 24px 40px;
  flex: 1;
  overflow-y: auto;
}

/* 滚动条美化 */
.cream-main::-webkit-scrollbar {
  width: 6px;
}

.cream-main::-webkit-scrollbar-thumb {
  background: #f5d7dc;
  border-radius: 10px;
}

.cream-main::-webkit-scrollbar-track {
  background: transparent;
}

/* ===== 聊天气泡布局 ===== */
.chat-message {
  display: flex;
  gap: 12px;
  margin: 18px 0;
  align-items: flex-end;
}

.chat-message.user {
  flex-direction: row-reverse;
}

/* 头像 */
.cream-avatar {
  border: 2px solid #fff;
  box-shadow: 0 4px 8px rgba(221, 207, 209, 0.2);
}

/* 气泡通用 */
.bubble {
  max-width: 650px;
  padding: 14px 18px;
  border-radius: 22px;
  line-height: 1.7;
  font-size: 14px;
  box-shadow: 0 4px 10px rgba(230, 215, 217, 0.15);
  transition: all 0.3s;
}

/* 用户气泡 - 浅粉奶油 */
.user .bubble {
  background: linear-gradient(135deg, #fddde6, #fef0f3);
  color: #8a7d7f;
  border-bottom-right-radius: 6px;
}

/* 机器人气泡 - 奶白浅蓝 */
.assistant .bubble {
  background: #f1eee9;
  color: #7a7072;
  border-bottom-left-radius: 6px;
}

/* 图表气泡 */
.chart-bubble {
  padding: 12px;
  background: #fafbfc !important;
}

/* ===== 底部输入区 ===== */
.cream-footer {
  background: transparent !important;
  padding: 16px 30px 30px;
  flex-shrink: 0;
  margin-bottom: 40px;
}

/* 仅修改：flex弹性布局，解决按钮挤压问题 */
.input-form {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  padding: 12px 18px;
  box-shadow: 0 6px 16px rgba(245, 224, 227, 0.15);
  backdrop-filter: blur(10px);
}
/* 仅新增：输入框占满剩余空间 */
.input-item {
  flex: 1;
  margin: 0 !important;
}

/* 仅修改：取消固定宽度，改为自适应100% */
.cream-input {
  width: 100% !important;
}

::v-deep(.el-textarea__inner) {
  border-radius: 18px;
  border: 1px solid #f5e1e4;
  background: #fffcfc;
  color: #8a7d7f;
  padding: 12px 16px;
  transition: all 0.3s;
}

::v-deep(.el-textarea__inner:focus) {
  border-color: #fddde6;
  box-shadow: 0 0 8px rgba(253, 221, 230, 0.3);
}

/* 发送按钮 */
.send-btn {
  border-radius: 18px;
  background: linear-gradient(135deg, #fddde6, #d1f2ff);
  border: none;
  color: #8a7d7f;
  height: 42px;
  padding: 0 24px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(253, 221, 230, 0.3);
  color: #d48892;
}
</style>
