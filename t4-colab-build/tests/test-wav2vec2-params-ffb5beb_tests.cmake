add_test( [==[wav2vec2: default params]==] /content/CrispASR-NB/t4-colab-build/bin/test-wav2vec2-params [==[wav2vec2: default params]==]  )
set_tests_properties( [==[wav2vec2: default params]==] PROPERTIES WORKING_DIRECTORY /content/CrispASR-NB/t4-colab-build/tests LABELS unit SKIP_RETURN_CODE 4)
set( test-wav2vec2-params_TESTS [==[wav2vec2: default params]==])
