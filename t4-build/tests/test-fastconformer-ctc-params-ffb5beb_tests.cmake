add_test( [==[fastconformer-ctc: default params]==] /kaggle/working/CrispASR-T4/t4-build/bin/test-fastconformer-ctc-params [==[fastconformer-ctc: default params]==]  )
set_tests_properties( [==[fastconformer-ctc: default params]==] PROPERTIES WORKING_DIRECTORY /kaggle/working/CrispASR-T4/t4-build/tests LABELS unit SKIP_RETURN_CODE 4)
set( test-fastconformer-ctc-params_TESTS [==[fastconformer-ctc: default params]==])
