FROM kodbasen/ruby-armhf
RUN apk add --update build-base
RUN gem install sinatra --no-ri --no-rdoc
RUN gem install thin
ADD hasher.rb /
CMD ["ruby", "hasher.rb"]
EXPOSE 80
