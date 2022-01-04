import sys
# Send integration test to py2 or py3 based on stuff

if __name__ == "__main__":
    version_major = sys.version_info[0]
    version_minor = sys.version_info[1]

    if version_major > 3 and version_minor > 6:
        import py3_integration
        py3_integration.run_test()

    else:
        import py2_integration
        py2_integration.run_test()