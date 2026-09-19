add_test( [==[Windows dshow mic arg uses the provided device name]==] /kaggle/working/CrispASR-T4/t4-build/bin/test-windows-mic [==[Windows dshow mic arg uses the provided device name]==]  )
set_tests_properties( [==[Windows dshow mic arg uses the provided device name]==] PROPERTIES WORKING_DIRECTORY /kaggle/working/CrispASR-T4/t4-build/tests LABELS unit windows SKIP_RETURN_CODE 4)
set( test-windows-mic_TESTS [==[Windows dshow mic arg uses the provided device name]==])
