LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := optional

LOCAL_SRC_FILES := Sample_Algorithm.cpp \
                   Sample_Math.cpp

LOCAL_MODULE:= libgtstsample

LOCAL_C_INCLUDES := build/core/templates/sample/googletest/include

include $(BUILD_SHARED_LIBRARY)
