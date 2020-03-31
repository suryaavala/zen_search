#!/bin/bash

pytest \
--verbose \
--cov=../zensearch ../tests \
--cov-report term-missing:skip-covered