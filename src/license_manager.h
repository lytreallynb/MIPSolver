// src/license_manager.h
#ifndef LICENSE_MANAGER_H
#define LICENSE_MANAGER_H

#include <string>
#include <chrono>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <algorithm>

#ifdef PLATFORM_WINDOWS
    #include <windows.h>
    #include <iphlpapi.h>
    #include <winsock2.h>
    #pragma comment(lib, "iphlpapi.lib")
    #pragma comment(lib, "ws2_32.lib")
#elif defined(PLATFORM_MACOS)
    #include <IOKit/IOKitLib.h>
    #include <IOKit/network/IOEthernetInterface.h>
    #include <IOKit/network/IONetworkInterface.h>
    #include <IOKit/network/IOEthernetController.h>
    #include <CoreFoundation/CoreFoundation.h>
    #include <sys/sysctl.h>
    // 处理macOS版本兼容性
    #ifndef kIOMainPortDefault
        #define kIOMainPortDefault kIOMasterPortDefault
    #endif
#elif defined(PLATFORM_LINUX)
    #include <fstream>
    #include <sys/ioctl.h>
    #include <net/if.h>
    #include <unistd.h>
    #include <netinet/in.h>
    #include <string.h>
#endif

namespace MIPSolver {

class HardwareID {
public:
    static std::string getMachineID() {
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
        std::string cpuid = getWindowsCPUID();
        if (!cpuid.empty()) {
            hwid += cpuid;
        }
        
        // 获取MAC地址
        std::string mac = getWindowsMACAddress();
        if (!mac.empty()) {
            hwid += "_" + mac;
        }
        
        // 获取磁盘序列号
        std::string disk = getWindowsDiskSerial();
        if (!disk.empty()) {
            hwid += "_" + disk;
        }
        
        return hwid;
    }
    
    static std::string getWindowsCPUID() {
        int cpuInfo[4] = {0};
        __cpuid(cpuInfo, 1);
        
        char buffer[64];
        sprintf_s(buffer, sizeof(buffer), "%08X%08X", cpuInfo[3], cpuInfo[0]);
        return std::string(buffer);
    }
    
    static std::string getWindowsMACAddress() {
        IP_ADAPTER_INFO adapterInfo[16];
        DWORD bufLen = sizeof(adapterInfo);
        
        DWORD status = GetAdaptersInfo(adapterInfo, &bufLen);
        if (status == ERROR_SUCCESS) {
            PIP_ADAPTER_INFO adapter = adapterInfo;
            while (adapter) {
                if (adapter->Type == MIB_IF_TYPE_ETHERNET) {
                    char buffer[32];
                    sprintf_s(buffer, sizeof(buffer), "%02X%02X%02X%02X%02X%02X",
                        adapter->Address[0], adapter->Address[1], adapter->Address[2],
                        adapter->Address[3], adapter->Address[4], adapter->Address[5]);
                    return std::string(buffer);
                }
                adapter = adapter->Next;
            }
        }
        return "";
    }
    
    static std::string getWindowsDiskSerial() {
        DWORD serialNumber;
        if (GetVolumeInformationA("C:\\", NULL, 0, &serialNumber, NULL, NULL, NULL, 0)) {
            char buffer[16];
            sprintf_s(buffer, sizeof(buffer), "%08X", serialNumber);
            return std::string(buffer);
        }
        return "";
    }
#endif

#ifdef PLATFORM_MACOS
    static std::string getMacOSHardwareID() {
        std::string hwid;
        
        // 获取硬件UUID
        std::string uuid = getMacOSSystemUUID();
        if (!uuid.empty()) {
            hwid += uuid;
        }
        
        // 获取MAC地址
        std::string mac = getMacOSMACAddress();
        if (!mac.empty()) {
            hwid += "_" + mac;
        }
        
        return hwid;
    }
    
    static std::string getMacOSSystemUUID() {
        // 使用兼容的主端口定义
        mach_port_t mainPort = kIOMainPortDefault;
        
        io_registry_entry_t ioRegistryRoot = IORegistryEntryFromPath(mainPort, "IOService:/");
        if (ioRegistryRoot == MACH_PORT_NULL) {
            return "";
        }
        
        CFStringRef uuidCf = (CFStringRef) IORegistryEntryCreateCFProperty(ioRegistryRoot,
                                                                          CFSTR(kIOPlatformUUIDKey),
                                                                          kCFAllocatorDefault, 0);
        IOObjectRelease(ioRegistryRoot);
        
        if (uuidCf) {
            char buffer[256];
            Boolean result = CFStringGetCString(uuidCf, buffer, sizeof(buffer), kCFStringEncodingUTF8);
            CFRelease(uuidCf);
            
            if (result) {
                return std::string(buffer);
            }
        }
        return "";
    }
    
    static std::string getMacOSMACAddress() {
        kern_return_t kernResult = KERN_SUCCESS;
        io_iterator_t intfIterator;
        mach_port_t mainPort = kIOMainPortDefault;
        
        kernResult = IOServiceGetMatchingServices(mainPort,
                                                IOServiceMatching(kIOEthernetInterfaceClass),
                                                &intfIterator);
        
        if (kernResult != KERN_SUCCESS) {
            return "";
        }
        
        io_object_t intfService;
        while ((intfService = IOIteratorNext(intfIterator))) {
            io_object_t controllerService;
            
            kernResult = IORegistryEntryGetParentEntry(intfService, kIOServicePlane, &controllerService);
            if (kernResult == KERN_SUCCESS) {
                CFTypeRef MACAddressAsCFData = IORegistryEntryCreateCFProperty(controllerService,
                                                                            CFSTR(kIOMACAddress),
                                                                            kCFAllocatorDefault, 0);
                if (MACAddressAsCFData) {
                    const UInt8* MACAddress = (const UInt8*)CFDataGetBytePtr((CFDataRef)MACAddressAsCFData);
                    char buffer[32];
                    // 使用snprintf代替sprintf
                    snprintf(buffer, sizeof(buffer), "%02X%02X%02X%02X%02X%02X",
                        MACAddress[0], MACAddress[1], MACAddress[2],
                        MACAddress[3], MACAddress[4], MACAddress[5]);
                    
                    CFRelease(MACAddressAsCFData);
                    IOObjectRelease(controllerService);
                    IOObjectRelease(intfService);
                    IOObjectRelease(intfIterator);
                    
                    return std::string(buffer);
                }
                IOObjectRelease(controllerService);
            }
            IOObjectRelease(intfService);
        }
        IOObjectRelease(intfIterator);
        
        return "";
    }
#endif

#ifdef PLATFORM_LINUX
    static std::string getLinuxHardwareID() {
        std::string hwid;
        
        // 获取机器ID
        std::string machineId = getLinuxMachineID();
        if (!machineId.empty()) {
            hwid += machineId;
        }
        
        // 获取MAC地址
        std::string mac = getLinuxMACAddress();
        if (!mac.empty()) {
            hwid += "_" + mac;
        }
        
        // 获取CPU信息
        std::string cpu = getLinuxCPUInfo();
        if (!cpu.empty()) {
            hwid += "_" + cpu;
        }
        
        return hwid;
    }
    
    static std::string getLinuxMachineID() {
        std::ifstream file("/etc/machine-id");
        if (file.is_open()) {
            std::string line;
            if (std::getline(file, line)) {
                return line;
            }
        }
        
        // 备选方案：尝试/var/lib/dbus/machine-id
        std::ifstream file2("/var/lib/dbus/machine-id");
        if (file2.is_open()) {
            std::string line;
            if (std::getline(file2, line)) {
                return line;
            }
        }
        
        return "";
    }
    
    static std::string getLinuxMACAddress() {
        std::ifstream file("/sys/class/net/eth0/address");
        if (file.is_open()) {
            std::string mac;
            if (std::getline(file, mac)) {
                // 移除冒号
                mac.erase(std::remove(mac.begin(), mac.end(), ':'), mac.end());
                std::transform(mac.begin(), mac.end(), mac.begin(), ::toupper);
                return mac;
            }
        }
        
        // 尝试其他网络接口
        for (const auto& iface : {"enp0s3", "ens33", "wlan0", "wlp2s0"}) {
            std::string path = "/sys/class/net/" + std::string(iface) + "/address";
            std::ifstream f(path);
            if (f.is_open()) {
                std::string mac;
                if (std::getline(f, mac)) {
                    mac.erase(std::remove(mac.begin(), mac.end(), ':'), mac.end());
                    std::transform(mac.begin(), mac.end(), mac.begin(), ::toupper);
                    return mac;
                }
            }
        }
        
        return "";
    }
    
    static std::string getLinuxCPUInfo() {
        std::ifstream file("/proc/cpuinfo");
        if (file.is_open()) {
            std::string line;
            while (std::getline(file, line)) {
                if (line.find("processor") == 0) {
                    size_t pos = line.find(":");
                    if (pos != std::string::npos) {
                        return line.substr(pos + 1);
                    }
                }
            }
        }
        return "";
    }
#endif
};

class LicenseManager {
public:
    struct License {
        std::string user_name;
        std::string license_type;  // "free", "pro", "enterprise"
        std::time_t expiry_date;
        std::string hardware_id;
        bool is_valid;
        
        License() : expiry_date(0), is_valid(false) {}
    };
    
    static bool initialize() {
        static bool initialized = false;
        if (!initialized) {
            license_ = loadLicense();
            initialized = true;
        }
        return license_.is_valid;
    }
    
    static bool checkLicense() {
        if (!initialize()) {
            return false;
        }
        
        // 检查过期时间
        auto now = std::chrono::system_clock::now();
        auto now_time_t = std::chrono::system_clock::to_time_t(now);
        
        if (license_.expiry_date > 0 && now_time_t > license_.expiry_date) {
            return false;  // 许可证过期
        }
        
        // 检查硬件绑定
        if (!license_.hardware_id.empty()) {
            std::string current_hwid = HardwareID::getMachineID();
            if (license_.hardware_id != current_hwid) {
                return false;  // 硬件不匹配
            }
        }
        
        return true;
    }
    
    static std::string getLicenseType() {
        if (!initialize()) {
            return "invalid";
        }
        return license_.license_type;
    }
    
    static std::string getUserName() {
        if (!initialize()) {
            return "unknown";
        }
        return license_.user_name;
    }
    
    static std::string getCurrentHardwareID() {
        return HardwareID::getMachineID();
    }

private:
    static License license_;
    
    static License loadLicense() {
        License license;
        
        // 尝试从几个位置加载许可证
        std::vector<std::string> license_paths = {
            "license.dat",
            "mipsolver_license.txt",
            "mipsolver.lic",
        };
        
        for (const auto& path : license_paths) {
            if (loadFromFile(path, license)) {
                break;
            }
        }
        
        // 如果没有找到许可证文件，使用免费版
        if (!license.is_valid) {
            license = createFreeLicense();
        }
        
        return license;
    }
    
    static bool loadFromFile(const std::string& filepath, License& license) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            return false;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            if (line.find("USER=") == 0) {
                license.user_name = line.substr(5);
            } else if (line.find("TYPE=") == 0) {
                license.license_type = line.substr(5);
            } else if (line.find("EXPIRY=") == 0) {
                license.expiry_date = std::stoll(line.substr(7));
            } else if (line.find("HWID=") == 0) {
                license.hardware_id = line.substr(5);
            }
        }
        
        // 简单验证
        if (!license.user_name.empty() && !license.license_type.empty()) {
            license.is_valid = true;
            return true;
        }
        
        return false;
    }
    
    static License createFreeLicense() {
        License license;
        license.user_name = "Free User";
        license.license_type = "free";
        license.expiry_date = 0;  // 永不过期
        license.hardware_id = "";
        license.is_valid = true;
        return license;
    }
};

// 静态成员定义
LicenseManager::License LicenseManager::license_;

} // namespace MIPSolver

#endif