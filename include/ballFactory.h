#pragma once

#include "wog2/json.h"
#include "wog2/templateInfo.h"
#include "wog2/ballFactory.h"

struct BallTemplateInfoExt : public BallTemplateInfo {
    ImageIdInfo editorButtonImageId;
};

class BallFactoryExt : public BallFactory {
public:
    BallTemplateInfoExt* getTemplateInfo(int typeEnum);
    BallTemplateInfoExt* getTemplateInfoOrNull(int typeEnum);
    
public:
    static BallFactoryExt* instance() {
        return (BallFactoryExt*)BallFactory::instance();
    }
};

extern "C" {
    size_t getTemplateInfoOffset(int i);
    bool BallTemplateInfo_deserializeExt(BallTemplateInfoExt* info, int ballType, const cJSON* json);
    void addGooballButtons();
}
