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
    echo "  clean           - 清理编译产出"
    echo "  compile         - 编译项目"
    echo "  package         - 打包项目"
    echo "  test            - 运行测试"
    echo "  run [mode] [args] - 运行程序，支持以下模式："
    echo "    asr <audio_file>     - 运行语音识别"
    echo "    register <audio_file> <speaker_name> - 注册声纹"
    echo "    search <audio_file>  - 搜索声纹"
    echo "    delete-all          - 删除所有声纹"
    echo "  all [mode] [args] - 清理、编译、打包并运行"
    echo
    echo "Examples:"
    echo "  $0 run asr /path/to/audio.wav"
    echo "  $0 run register /path/to/audio.wav speaker_name"
    echo "  $0 run search /path/to/audio.wav"
    echo "  $0 run delete-all"
    echo "  $0 all asr /path/to/audio.wav"
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
    if [ ! -f target/realtime_asr_voiceid-1.0-SNAPSHOT.jar ]; then
        echo -e "${RED}JAR file not found. Please run 'package' first.${NC}"
        exit 1
    fi
}

# 运行程序
run_program() {
    local mode=$1
    shift  # 移除第一个参数（mode）
    
    check_jar
    echo -e "${GREEN}Running program in $mode mode${NC}"
    java -jar target/realtime_asr_voiceid-1.0-SNAPSHOT.jar "$mode" "$@"
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
            echo -e "${RED}Error: Mode is required${NC}"
            show_help
            exit 1
        fi
        
        mode=$2
        shift 2  # 移除 "run" 和 mode 参数
        
        case "$mode" in
            "asr")
                if [ -z "$1" ]; then
                    echo -e "${RED}Error: Audio file path is required for ASR mode${NC}"
                    show_help
                    exit 1
                fi
                run_program "asr" "$@"
                ;;
            "register")
                if [ -z "$1" ] || [ -z "$2" ]; then
                    echo -e "${RED}Error: Audio file path and speaker name are required for register mode${NC}"
                    show_help
                    exit 1
                fi
                run_program "register" "$@"
                ;;
            "search")
                if [ -z "$1" ]; then
                    echo -e "${RED}Error: Audio file path is required for search mode${NC}"
                    show_help
                    exit 1
                fi
                run_program "search" "$@"
                ;;
            "delete-all")
                run_program "delete-all"
                ;;
            *)
                echo -e "${RED}Error: Unknown mode: $mode${NC}"
                show_help
                exit 1
                ;;
        esac
        ;;
        
    "all")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Mode is required${NC}"
            show_help
            exit 1
        fi
        
        echo -e "${GREEN}Building and running project...${NC}"
        run_maven clean package
        
        mode=$2
        shift 2  # 移除 "all" 和 mode 参数
        run_program "$mode" "$@"
        ;;
        
    *)
        show_help
        exit 1
        ;;
esac

exit 0