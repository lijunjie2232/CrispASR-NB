add_test( [==[fastconformer-ctc: default params]==] /content/CrispASR-NB/t4-colab-build/bin/test-fastconformer-ctc-params [==[fastconformer-ctc: default params]==]  )
set_tests_properties( [==[fastconformer-ctc: default params]==] PROPERTIES WORKING_DIRECTORY /content/CrispASR-NB/t4-colab-build/tests LABELS unit SKIP_RETURN_CODE 4)
set( test-fastconformer-ctc-params_TESTS [==[fastconformer-ctc: default params]==])
