LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := tests

#EMMA_INSTRUMENT=true
#EMMA_INSTRUMENT_STATIC=true 

LOCAL_SRC_FILES := $(call all-java-files-under, src)

LOCAL_PACKAGE_NAME := FooTest

LOCAL_JAVA_LIBRARIES := android.test.runner

LOCAL_STATIC_JAVA_LIBRARIES := ub-uiautomator junit legacy-android-test android-support-test com.example.foo

LOCAL_CERTIFICATE := platform

LOCAL_JACK_COVERAGE_INCLUDE_FILTER := com.example.foo.Foo

LOCAL_PRIVATE_PLATFORM_APIS := true

include $(BUILD_PACKAGE)

include $(call all-makefiles-under,$(LOCAL_PATH))
