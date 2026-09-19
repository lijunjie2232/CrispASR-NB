add_test( [==[Windows dshow mic arg uses the provided device name]==] /content/CrispASR-NB/t4-colab-build/bin/test-windows-mic [==[Windows dshow mic arg uses the provided device name]==]  )
set_tests_properties( [==[Windows dshow mic arg uses the provided device name]==] PROPERTIES WORKING_DIRECTORY /content/CrispASR-NB/t4-colab-build/tests LABELS unit windows SKIP_RETURN_CODE 4)
set( test-windows-mic_TESTS [==[Windows dshow mic arg uses the provided device name]==])
