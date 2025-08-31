FROM python:3.12-slim
WORKDIR /app

COPY vendor/linux_wheels /wheels
RUN python -m venv /venv \
 && /venv/bin/pip install --no-index --find-links /wheels csvkit agate agate-excel openpyxl xlrd \
 && for f in /venv/bin/csv*; do ln -sf "$f" "/usr/local/bin/$(basename "$f")"; done

# (PATH still helps, but symlinks make it robust)
ENV PATH=/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

COPY samples /app/samples
