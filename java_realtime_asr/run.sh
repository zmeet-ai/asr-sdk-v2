#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}Usage: $0 [command] [args]${NC}"
    echo "Commands:"
    echo "  clean      - 清理编译产出"
    echo "  compile    - 编译项目"
    echo "  package    - 打包项目"
    echo "  test       - 运行测试"
    echo "  run [file] - 运行程序 (需要指定音频文件路径)"
    echo "  all [file] - 清理、编译、打包并运行 (需要指定音频文件路径)"
    echo
    echo "Example:"
    echo "  $0 run /path/to/audio.wav"
    echo "  $0 all /path/to/audio.wav"
}

# 执行 Maven 命令并检查结果
run_maven() {
    mvn "$@"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Maven command failed: mvn $@${NC}"
        exit 1
    fi
}

# 检查 jar 文件是否存在
check_jar() {
    if [ ! -f target/realtime_asr-1.0-SNAPSHOT.jar ]; then
        echo -e "${RED}JAR file not found. Please run 'package' first.${NC}"
        exit 1
    fi
}

# 主命令处理
case "$1" in
    "clean")
        echo -e "${GREEN}Cleaning project...${NC}"
        run_maven clean
        ;;
        
    "compile")
        echo -e "${GREEN}Compiling project...${NC}"
        run_maven compile
        ;;
        
    "package")
        echo -e "${GREEN}Packaging project...${NC}"
        run_maven clean package
        ;;
        
    "test")
        echo -e "${GREEN}Running tests...${NC}"
        run_maven test
        ;;
        
    "run")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Audio file path is required${NC}"
            show_help
            exit 1
        fi
        
        check_jar
        echo -e "${GREEN}Running ASR client with audio file: $2${NC}"
        java -jar target/realtime_asr-1.0-SNAPSHOT.jar "$2"
        ;;
        
    "all")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Audio file path is required${NC}"
            show_help
            exit 1
        fi
        
        echo -e "${GREEN}Building and running project...${NC}"
        run_maven clean package
        echo -e "${GREEN}Running ASR client with audio file: $2${NC}"
        java -jar target/realtime_asr-1.0-SNAPSHOT.jar "$2"
        ;;
        
    *)
        show_help
        exit 1
        ;;
esac

exit 0