// tools/license_generator.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

// 包含硬件ID获取功能（复制自license_manager.h中的相关部分）
#ifdef PLATFORM_WINDOWS
    #include <windows.h>
    #include <iphlpapi.h>
    #include <winsock2.h>
    #include <intrin.h>
    #pragma comment(lib, "iphlpapi.lib")
    #pragma comment(lib, "ws2_32.lib")
#elif defined(PLATFORM_MACOS)
    #include <IOKit/IOKitLib.h>
    #include <IOKit/network/IOEthernetInterface.h>
    #include <IOKit/network/IONetworkInterface.h>
    #include <IOKit/network/IOEthernetController.h>
    #include <CoreFoundation/CoreFoundation.h>
    #include <sys/sysctl.h>
#elif defined(PLATFORM_LINUX)
    #include <fstream>
    #include <sys/ioctl.h>
    #include <net/if.h>
    #include <unistd.h>
    #include <netinet/in.h>
    #include <string.h>
    #include <algorithm>
#endif

struct LicenseInfo {
    std::string user_name;
    std::string license_type;  // "free", "pro", "enterprise"
    int validity_days;         // 有效期天数，0表示永久
    std::string hardware_id;   // 硬件ID，空表示不绑定硬件
    bool bind_hardware;        // 是否绑定当前机器硬件
};

class HardwareIDGenerator {
public:
    static std::string getCurrentMachineID() {
        std::string hwid;
        
#ifdef PLATFORM_WINDOWS
        hwid = getWindowsHardwareID();
#elif defined(PLATFORM_MACOS)
        hwid = getMacOSHardwareID();
#elif defined(PLATFORM_LINUX)
        hwid = getLinuxHardwareID();
#else
        hwid = "unknown_platform";
#endif
        
        return hwid.empty() ? "generic_hardware" : hwid;
    }

private:
#ifdef PLATFORM_WINDOWS
    static std::string getWindowsHardwareID() {
        std::string hwid;
        
        // 获取CPU ID
        int cpuInfo[4] = {0};
        __cpuid(cpuInfo, 1);
        char cpuBuffer[64];
        sprintf_s(cpuBuffer, sizeof(cpuBuffer), "%08X%08X", cpuInfo[3], cpuInfo[0]);
        hwid += std::string(cpuBuffer);
        
        // 获取MAC地址
        IP_ADAPTER_INFO adapterInfo[16];
        DWORD bufLen = sizeof(adapterInfo);
        DWORD status = GetAdaptersInfo(adapterInfo, &bufLen);
        if (status == ERROR_SUCCESS) {
            PIP_ADAPTER_INFO adapter = adapterInfo;
            while (adapter) {
                if (adapter->Type == MIB_IF_TYPE_ETHERNET) {
                    char macBuffer[32];
                    sprintf_s(macBuffer, sizeof(macBuffer), "%02X%02X%02X%02X%02X%02X",
                        adapter->Address[0], adapter->Address[1], adapter->Address[2],
                        adapter->Address[3], adapter->Address[4], adapter->Address[5]);
                    hwid += "_" + std::string(macBuffer);
                    break;
                }
                adapter = adapter->Next;
            }
        }
        
        return hwid;
    }
#endif

#ifdef PLATFORM_MACOS
    static std::string getMacOSHardwareID() {
        std::string hwid;
        
        // 获取系统UUID
        io_registry_entry_t ioRegistryRoot = IORegistryEntryFromPath(kIOMasterPortDefault, "IOService:/");
        CFStringRef uuidCf = (CFStringRef) IORegistryEntryCreateCFProperty(ioRegistryRoot,
                                                                          CFSTR(kIOPlatformUUIDKey),
                                                                          kCFAllocatorDefault, 0);
        IOObjectRelease(ioRegistryRoot);
        
        if (uuidCf) {
            char buffer[256];
            Boolean result = CFStringGetCString(uuidCf, buffer, sizeof(buffer), kCFStringEncodingUTF8);
            CFRelease(uuidCf);
            if (result) {
                hwid += std::string(buffer);
            }
        }
        
        return hwid;
    }
#endif

#ifdef PLATFORM_LINUX
    static std::string getLinuxHardwareID() {
        std::string hwid;
        
        // 获取机器ID
        std::ifstream file("/etc/machine-id");
        if (file.is_open()) {
            std::string line;
            if (std::getline(file, line)) {
                hwid += line;
            }
        }
        
        // 获取MAC地址
        std::ifstream macFile("/sys/class/net/eth0/address");
        if (macFile.is_open()) {
            std::string mac;
            if (std::getline(macFile, mac)) {
                mac.erase(std::remove(mac.begin(), mac.end(), ':'), mac.end());
                std::transform(mac.begin(), mac.end(), mac.begin(), ::toupper);
                hwid += "_" + mac;
            }
        }
        
        return hwid;
    }
#endif
};

std::time_t calculateExpiryDate(int validity_days) {
    if (validity_days <= 0) {
        return 0;  // 永不过期
    }
    
    auto now = std::chrono::system_clock::now();
    auto expiry = now + std::chrono::hours(24 * validity_days);
    return std::chrono::system_clock::to_time_t(expiry);
}

std::string formatDate(std::time_t timestamp) {
    if (timestamp == 0) {
        return "Never expires";
    }
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&timestamp), "%Y-%m-%d");
    return ss.str();
}

bool generateLicense(const LicenseInfo& info, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Cannot create license file: " << filename << std::endl;
        return false;
    }
    
    std::time_t expiry = calculateExpiryDate(info.validity_days);
    std::string hardware_id = info.hardware_id;
    
    // 如果要求绑定硬件，获取当前机器的硬件ID
    if (info.bind_hardware) {
        hardware_id = HardwareIDGenerator::getCurrentMachineID();
        std::cout << "Current machine hardware ID: " << hardware_id << std::endl;
    }
    
    // 写入许可证信息
    file << "# MIPSolver License File" << std::endl;
    file << "# Generated on: " << formatDate(std::chrono::system_clock::to_time_t(std::chrono::system_clock::now())) << std::endl;
    file << "# Do not modify this file" << std::endl;
    file << std::endl;
    
    file << "USER=" << info.user_name << std::endl;
    file << "TYPE=" << info.license_type << std::endl;
    file << "EXPIRY=" << expiry << std::endl;
    file << "HWID=" << hardware_id << std::endl;
    
    // 简单的校验和
    size_t checksum = std::hash<std::string>{}(info.user_name + info.license_type + std::to_string(expiry) + hardware_id);
    file << "CHECKSUM=" << checksum << std::endl;
    
    file.close();
    return true;
}

void printUsage(const char* program_name) {
    std::cout << "MIPSolver License Generator" << std::endl;
    std::cout << std::endl;
    std::cout << "Usage: " << program_name << " [options]" << std::endl;
    std::cout << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --user <name>         User name" << std::endl;
    std::cout << "  --type <type>         License type (free/pro/enterprise)" << std::endl;
    std::cout << "  --days <days>         Validity period in days (0=permanent)" << std::endl;
    std::cout << "  --hwid <hardware_id>  Hardware ID (optional)" << std::endl;
    std::cout << "  --bind-current        Bind to current machine hardware" << std::endl;
    std::cout << "  --output <filename>   Output filename" << std::endl;
    std::cout << "  --show-hwid           Show current machine hardware ID and exit" << std::endl;
    std::cout << "  --help                Show this help" << std::endl;
    std::cout << std::endl;
    std::cout << "Examples:" << std::endl;
    std::cout << "  " << program_name << " --user \"John Doe\" --type pro --days 365 --output license.dat" << std::endl;
    std::cout << "  " << program_name << " --user \"ABC Corp\" --type enterprise --days 0 --bind-current" << std::endl;
    std::cout << "  " << program_name << " --show-hwid" << std::endl;
}

int main(int argc, char* argv[]) {
    LicenseInfo info;
    std::string output_file = "mipsolver_license.txt";
    bool show_hwid_only = false;
    
    // 默认值
    info.license_type = "free";
    info.validity_days = 365;
    info.bind_hardware = false;
    
    // 解析命令行参数
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "--show-hwid") {
            show_hwid_only = true;
        } else if (arg == "--user" && i + 1 < argc) {
            info.user_name = argv[++i];
        } else if (arg == "--type" && i + 1 < argc) {
            info.license_type = argv[++i];
        } else if (arg == "--days" && i + 1 < argc) {
            info.validity_days = std::stoi(argv[++i]);
        } else if (arg == "--hwid" && i + 1 < argc) {
            info.hardware_id = argv[++i];
        } else if (arg == "--bind-current") {
            info.bind_hardware = true;
        } else if (arg == "--output" && i + 1 < argc) {
            output_file = argv[++i];
        }
    }
    
    // 如果只是要显示硬件ID
    if (show_hwid_only) {
        std::string hwid = HardwareIDGenerator::getCurrentMachineID();
        std::cout << "Current machine hardware ID: " << hwid << std::endl;
        std::cout << "Platform: ";
#ifdef PLATFORM_WINDOWS
        std::cout << "Windows";
#elif defined(PLATFORM_MACOS)
        std::cout << "macOS";
#elif defined(PLATFORM_LINUX)
        std::cout << "Linux";
#else
        std::cout << "Unknown";
#endif
        std::cout << std::endl;
        return 0;
    }
    
    // 验证输入
    if (info.user_name.empty()) {
        std::cerr << "Error: User name is required" << std::endl;
        printUsage(argv[0]);
        return 1;
    }
    
    if (info.license_type != "free" && info.license_type != "pro" && info.license_type != "enterprise") {
        std::cerr << "Error: Invalid license type. Supported: free, pro, enterprise" << std::endl;
        return 1;
    }
    
    // 生成许可证
    std::cout << "Generating license..." << std::endl;
    std::cout << "User: " << info.user_name << std::endl;
    std::cout << "Type: " << info.license_type << std::endl;
    std::cout << "Validity: " << (info.validity_days == 0 ? "Permanent" : std::to_string(info.validity_days) + " days") << std::endl;
    
    if (info.bind_hardware || !info.hardware_id.empty()) {
        std::cout << "Hardware binding: Yes" << std::endl;
    } else {
        std::cout << "Hardware binding: No" << std::endl;
    }
    
    std::cout << "Output file: " << output_file << std::endl;
    
    if (generateLicense(info, output_file)) {
        std::cout << std::endl;
        std::cout << "License generated successfully!" << std::endl;
        std::cout << "File saved as: " << output_file << std::endl;
        
        std::time_t expiry = calculateExpiryDate(info.validity_days);
        if (expiry > 0) {
            std::cout << "Expiry date: " << formatDate(expiry) << std::endl;
        }
        
        std::cout << std::endl;
        std::cout << "Usage instructions:" << std::endl;
        std::cout << "   Place this file in the same directory as MIPSolver to activate the license." << std::endl;
        
        return 0;
    } else {
        std::cerr << "License generation failed" << std::endl;
        return 1;
    }
}

/*
Compilation instructions:

Windows (Visual Studio):
cl /EHsc /DPLATFORM_WINDOWS license_generator.cpp /Fe:licgen.exe

Linux:
g++ -std=c++17 -DPLATFORM_LINUX license_generator.cpp -o licgen

macOS:
g++ -std=c++17 -DPLATFORM_MACOS license_generator.cpp -framework IOKit -framework CoreFoundation -o licgen

Usage examples:

1. Show current machine hardware ID:
   ./licgen --show-hwid

2. Generate free license:
   ./licgen --user "Test User" --type free --days 30

3. Generate professional license:
   ./licgen --user "John Doe" --type pro --days 365 --output license.dat

4. Generate enterprise license bound to current machine:
   ./licgen --user "ABC Company" --type enterprise --days 0 --bind-current

5. Generate license with specific hardware ID:
   ./licgen --user "Remote User" --type pro --days 365 --hwid "ABC123DEF456"
*/