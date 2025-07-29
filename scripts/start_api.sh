#!/bin/bash
echo "启动MIPSolver API服务器..."
echo "访问 http://localhost:8080 查看API文档"
python api_server.py --host 0.0.0.0 --port 8080