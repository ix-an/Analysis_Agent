from fastapi import APIRouter, Request
from app.api.schema.login_schema import SendCodeSchema, LoginSchema
from app.utils.Logger import Logger
import redis
import random

# 创建日志记录器
logger = Logger.get_logger(__name__)
# 创建路由
system_router = APIRouter()
# 创建 Redis 连接
redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True  # 解码 Redis 响应为字符串
)

# 随机生成验证码
def generate_code():
    return str(random.randint(1000, 9999))

# 定义发送验证码接口
@system_router.post("/send_code")
def send_code(request: Request, args: SendCodeSchema):
    # 获取智能体实例
    agent = request.app.state.system_agent
    # 随机生成验证码
    code = generate_code()
    # 把验证码传给智能体
    result = agent.answer(args.email, code)

    # 将验证码存入 Redis，过期时间为 1分钟
    key = f"{args.email}:login_code"
    redis_client.set(key, code, ex=60)

    logger.info(f"验证码已发送，并存入Redis")
    return {"code": result["code"], "msg": result["msg"]}

# 定义登录接口
@system_router.post("/login")
def login(args: LoginSchema):
    # 从 Redis 中获取验证码
    key = f"{args.email}:login_code"
    cache_code = redis_client.get(key)

    # 验证码不存在 = 过期
    if not cache_code:
        logger.info(f"尝试登录邮箱{args.email}，验证码不存在")
        return {"code": 500, "msg": "验证码已过期，请重新获取"}

    # 校验
    if cache_code == args.code:
        logger.info(f"尝试登录邮箱{args.email}，验证码正确")
        # 删除验证码
        redis_client.delete(key)
        return {"code": 200, "msg": "登录成功"}
    else:
        logger.info(f"尝试登录邮箱{args.email}，验证码错误")

    return {"code": 500, "msg": "验证码错误"}

# 定义发送注册验证码接口
@system_router.post("/send_register_code")
def send_register_code(request: Request, args: SendCodeSchema):
    # 获取智能体实例
    agent = request.app.state.system_agent
    # 随机生成验证码
    code = generate_code()
    # 把验证码传给注册智能体
    result = agent.register(args.email, code)

    # 将验证码存入 Redis，过期时间为 1分钟
    key = f"{args.email}:register_code"
    redis_client.set(key, code, ex=60)

    return {"code": result["code"], "msg": result["msg"]}

# 定义注册接口
@system_router.post("/register")
def register(args: LoginSchema):
    # 从 Redis 中获取注册验证码
    key = f"{args.email}:register_code"
    cache_code = redis_client.get(key)

    # 验证码不存在 = 过期
    if not cache_code:
        logger.info(f"尝试注册邮箱{args.email}，验证码不存在")
        return {"code": 500, "msg": "验证码已过期，请重新获取"}

    # 校验
    if cache_code == args.code:
        logger.info(f"尝试注册邮箱{args.email}，验证码正确")
        # 删除验证码
        redis_client.delete(key)
        return {"code": 200, "msg": "注册成功"}
    else:
        logger.info(f"尝试注册邮箱{args.email}，验证码错误")

    return {"code": 500, "msg": "验证码错误"}
