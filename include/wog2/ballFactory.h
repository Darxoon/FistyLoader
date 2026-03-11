#pragma once

#include "wog2/misc.h" // IWYU pragma: keep (it exports std::string, which clangd doesn't realize)

#define BASE_GOOBALL_COUNT 39

template<typename TemplateInfo>
struct BallFactory {
public:
    static BallFactory<TemplateInfo>* instance();
    
    virtual void destructorWorkaround();
    
    TemplateInfo* getTemplateInfo(int typeEnum);
    TemplateInfo* getTemplateInfo(const std::string& id);
    
    // custom method
    TemplateInfo* getTemplateInfoUnchecked(int typeEnum);
    
private:
    TemplateInfo* m_templateInfos;
    int m_ballCount;
    
    // originally, there would be a static array here
    // with the asm patches, this data structure is dynamically sized :D
};

extern "C" {
    const char* GetGooBallName(int typeEnum);
    void AddGooballButton(const char* name, int category, int category2, int typeEnum, const char* imageId, int unknown);
}
