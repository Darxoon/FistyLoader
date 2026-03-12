#pragma once

#include "wog2/misc.h" // IWYU pragma: keep (it exports std::string, which clangd doesn't realize)
#include "wog2/templateInfo.h"

#define BASE_GOOBALL_COUNT 39

struct BallFactory {
public:
    static BallFactory* instance();
    
    virtual void destructorWorkaround();
    
    BallTemplateInfo* getTemplateInfo(int typeEnum);
    BallTemplateInfo* getTemplateInfo(const std::string& id);
    
protected:
    BallTemplateInfo* m_rawTemplateInfos;
    int m_ballCount;
    
    // originally, there would be a static array here
    // with the asm patches, this data structure is dynamically sized :D
};

extern "C" {
    const char* GetGooBallName(int typeEnum);
    void AddGooballButton(const char* name, int category, int category2, int typeEnum, const char* imageId, int unknown);
}
