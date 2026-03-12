#pragma once

#include "wog2/json.h"
#include "wog2/templateInfo.h"
#include "wog2/ballFactory.h"

class BallFactoryExt : public BallFactory {
public:
    BallTemplateInfo* getTemplateInfo(int typeEnum);
    BallTemplateInfo* getTemplateInfoOrNull(int typeEnum);
};

static_assert(sizeof(BallFactoryExt) == sizeof(BallFactory));

struct BallTemplateInfoExt : public BallTemplateInfo {
    ImageIdInfo editorButtonImageId;
};

extern "C" {
    size_t getTemplateInfoOffset(int i);
    bool BallTemplateInfo_deserializeExt(BallTemplateInfoExt* info, int ballType, const cJSON* json);
    void addGooballButtons();
}
