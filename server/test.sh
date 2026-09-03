#!/usr/bin/bash

for i in {1..10};do
	uv run pytest;
	sleep 2s;
done
