add_test( [==[wav2vec2: default params]==] /kaggle/working/CrispASR-T4/t4-build/bin/test-wav2vec2-params [==[wav2vec2: default params]==]  )
set_tests_properties( [==[wav2vec2: default params]==] PROPERTIES WORKING_DIRECTORY /kaggle/working/CrispASR-T4/t4-build/tests LABELS unit SKIP_RETURN_CODE 4)
set( test-wav2vec2-params_TESTS [==[wav2vec2: default params]==])
