#include "wog2/templateInfo.h"
#include "wog2/ballFactory.h"
#include "wog2/json.h"

#include "ballFactory.h"
#include "ballTable.h"
#include "log.h"

// this overrides the original getTemplateInfo
// to extend for error handling and unhardcode BallTemplateInfo size
BallTemplateInfo* BallFactoryExt::getTemplateInfo(int typeEnum) {
    BallTemplateInfoExt* templateInfos = (BallTemplateInfoExt*)m_rawTemplateInfos;
    
    if (typeEnum < 0 || typeEnum >= gooballCount || !templateInfos[typeEnum].isInitialized()) {
        PRINT("Loading typeEnum %d (out of %d): %s\n", typeEnum, gooballCount,
            typeEnum > 0 && typeEnum < gooballCount ? templateInfos[typeEnum].name : "N/A");
        
        char buffer[0x40];
        snprintf(buffer, sizeof(buffer),
            "Error loading gooball:\n"
            "Unknown typeEnum %d.\n", typeEnum);
        
        SDL_ShowSimpleMessageBox(0x10, "Fisty Loader", buffer, 0);
        return nullptr;
    }
    
    return &templateInfos[typeEnum];
}

BallTemplateInfo* BallFactoryExt::getTemplateInfoOrNull(int typeEnum) {
    BallTemplateInfoExt* templateInfos = (BallTemplateInfoExt*)m_rawTemplateInfos;
    
    if (typeEnum < 0 || typeEnum >= gooballCount || !templateInfos[typeEnum].isInitialized()) {
        return nullptr;
    }
    
    return &templateInfos[typeEnum];
}

extern "C" {

size_t getTemplateInfoOffset(int i) {
    return i * sizeof(BallTemplateInfoExt);
}

// in the same order as the default gooball buttons
static int defaultGooballButtons[] = {
    1, 2, 4, 0xb, 3, 0x11, 6, 8, 0xe, 0xc, 7, 0xd,
    9, 0x10, 0x17, 0x19, 0x1a, 0xf, 0x20, 0x21, 5,
    0x22, 0x23, 0x25, 0x12, 0x26, 0x13, 0x1b, 0x1c,
};

static int defaultUnusedGooballButtons[] = { 10, 20, 29, 30 };

static const char* defaultEditorButtonImage(int ballType) {
    switch (ballType) {
        case 1:    return "IMAGE_EDITOR_UI_BALLCOMMON";
        case 2:    return "IMAGE_EDITOR_UI_BALLALBINO";
        case 4:    return "IMAGE_EDITOR_UI_BALLBALLOON";
        case 0xb:  return "IMAGE_EDITOR_UI_BALLBALLOONEYE";
        case 3:    return "IMAGE_EDITOR_UI_BALLIVY";
        case 0x11: return "IMAGE_EDITOR_UI_BALLROPE";
        case 6:    return "IMAGE_EDITOR_UI_BALLANCHOR";
        case 8:    return "IMAGE_EDITOR_UI_BALLGOOPRODUCT";
        case 0xe:  return "IMAGE_EDITOR_UI_BALLGOOPRODUCTWHITE";
        case 0xc:  return "IMAGE_EDITOR_UI_BALLCONDUIT";
        case 7:    return "IMAGE_EDITOR_UI_BALLLAUNCHERL2B";
        case 0xd:  return "IMAGE_EDITOR_UI_BALLLAUNCHERL2L";
        case 9:    return "IMAGE_EDITOR_UI_BALLTHRUSTER";
        case 0x10: return "IMAGE_EDITOR_UI_BALLSTICKYBOMB";
        case 0x17: return "IMAGE_EDITOR_UI_BALLMATCHSTICK";
        case 0x19: return "IMAGE_EDITOR_UI_BALLFIREWORKS";
        case 0x1a: return "IMAGE_EDITOR_UI_LIGHTBALL";
        case 0xf:  return "IMAGE_EDITOR_UI_BALLGROW";
        case 0x20: return "IMAGE_EDITOR_UI_BALLSHRINK";
        case 0x21: return "IMAGE_EDITOR_UI_BALLJELLY";
        case 5:    return "IMAGE_EDITOR_UI_BALLGOOLFSINGLE";
        case 0x22: return "IMAGE_EDITOR_UI_BALLGOOLF";
        case 0x23: return "IMAGE_EDITOR_UI_BALLTHISWAYUP";
        case 0x25: return "IMAGE_EDITOR_UI_BALLEYE";
        case 0x12: return "IMAGE_EDITOR_UI_BALLBOUNCY";
        case 0x26: return "IMAGE_EDITOR_UI_BALLGOOPRODUCT";
        case 0x13: return "IMAGE_EDITOR_UI_BALLFISH";
        case 0x1b: return "IMAGE_EDITOR_UI_BALLFIREWORKS";
        case 0x1c: return "IMAGE_EDITOR_UI_BALLFIREWORKS";
        
        default:   return nullptr;
    }
}

bool BallTemplateInfo_deserializeExt(BallTemplateInfoExt* info, int ballType, const cJSON* json) {
    cJSON* editorButtonImage = cJSON_GetObjectItemCaseSensitive(json, "editorButtonImage");
    
    const char* defaultEditorButton = defaultEditorButtonImage(ballType);
    if (defaultEditorButton != nullptr) {
        strncpy(info->editorButtonImageId.imageId, defaultEditorButton, 0x40);
    }
    
    if (editorButtonImage != nullptr) {
        if (!cJSON_IsObject(editorButtonImage))
            return false;
        
        if (!GetImageIdInfo(info->editorButtonImageId, editorButtonImage))
            return false;
    }
    
    PRINT("deserializing gooball %d %s: %s\n", ballType, info->name, info->editorButtonImageId.imageId);
    
    return true;
}

static void tryAddButton(BallFactoryExt* ballFactory, int typeEnum) {
    BallTemplateInfoExt* info = (BallTemplateInfoExt*)ballFactory->getTemplateInfoOrNull(typeEnum);
    if (info == nullptr)
        return;
    
    const char* editorButtonImageId = info->editorButtonImageId.imageId;
    if (editorButtonImageId[0] == '\0')
        return;
    
    const char* gooballName = GetGooBallName(typeEnum);
    AddGooballButton(gooballName, 0, 1, typeEnum, editorButtonImageId, 0);
}

void addGooballButtons() {
    BallFactoryExt* ballFactory = (BallFactoryExt*)BallFactory::instance();
    
    for (int i : defaultGooballButtons) {
        tryAddButton(ballFactory, i);
    }
    
    for (int i : defaultUnusedGooballButtons) {
        tryAddButton(ballFactory, i);
    }
    
    for (int i = BASE_GOOBALL_COUNT; i < gooballCount; i++) {
        tryAddButton(ballFactory, i);
    }
}

}
