LOCAL_PATH:= $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := tests

standard_src_tests := Test_Sample_Algorithm.cpp \
                      Test_Sample_Math.cpp


LOCAL_SRC_FILES := $(standard_src_tests)

LOCAL_MODULE:= gtstsample

LOCAL_C_INCLUDES := externals/icu4c/common/ \
                    externals/googletest/include/ \
                    build/core/templates/sample/googletest/include/ \

LOCAL_SHARED_LIBRARIES := libgtest libgtstsample

LOCAL_STATIC_LIBRARIES := libgtest_main

LOCAL_LDFLAGS := -lpthread -lrt -ldl

include $(BUILD_EXECUTABLE)
