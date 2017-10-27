REPO  ?= wireservice
IMG    = $(REPO)/csvkit
SRC    = $(wildcard csvkit/*.py) $(wildcard csvkit/convert/*.py) $(wildcard csvkit/utilities/*py)

clean:
	@rm -f .image

image:  .image
.image: Dockerfile requirements-py2.txt $(SRC)
	@docker build -t $(IMG) .
	@touch $@

push: .image
	@docker push $(IMG)

.PHONY: clean image push
