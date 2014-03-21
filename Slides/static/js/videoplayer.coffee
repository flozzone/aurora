class @Videoplayer
  constructor: (@directory, @url, @clip, @chapters) ->
    @activeChapter = -1
    @loaded = false
    @loading = false
    @label = $("#flowplayer_controls_label")
    @play = $("#flowplayer_controls_play")
    @prev = $("#flowplayer_controls_prev")
    @next = $("#flowplayer_controls_next")
    @whereAmI = $("#flowplayer_controls_where_am_i")
    @play.click =>
      @load(0)
    @setControllerState "play_only"
    
    #@prev = $("#flowplayer_controls_play")
  
  load: (chapter=0) ->
    $f "flowplayer_invisible", @directory + 'flowplayer-3.2.16.swf',
      debug: false
      clip:
        url: @clip
        debug: false
        provider: 'rtmp'
        autoPlay: true
        autoBuffering: true
        onStart: =>
          @loaded = true      
          @setState("active")
          @seekToChapter(chapter)
      plugins:
        rtmp:
          url: @directory + 'flowplayer.rtmp-3.2.12.swf'
          netConnectionUrl: @url
    
  setControllerState: (state) ->
    @resetControllerState()
    switch state
      when "play_only"
        @label.text "Play Audio"
        @play.removeClass "disabled"
      when "loading"
        @label.text "Loading"
        @play.removeClass "disabled"
        @play.addClass "loading"
      when "active"
        @label.text "Playing"
        @prev.removeClass "disabled"
        @play.removeClass "disabled"
        @play.removeClass "loading"        
        @next.removeClass "disabled"
        @whereAmI.removeClass "disabled"
      when "error"
        @play.text "Error"
        @play.text "ERROR"
      
  resetControllerState: ->
    @prev.addClass "disabled"
    @play.addClass "disabled"
    @next.addClass "disabled"
    @whereAmI.addClass "disabled"
  
  seekChapter: (chapter) ->
    console.log("seeking to chapter: " + chapter)
    
  togglePlay: ->
    if not @loading
      if loaded
        if $().isPlaying
          @pause()
        else
          @play()
      else
        @setControllerState "loading"
        @loading = true
        @load
    
  play: ->
    @play.text "PAUSE"
    $f.play()
    
  pause: ->
    @play.text "PLAY"
    $f.pause()
    
  prev: ->
    console.log("previous chapter")
    
  next: ->
    console.log("next chapter")
    
    
    
#       $f("flowplayer_invisible", media_url + "slidecasting-media/flowplayer/flowplayer-3.2.16.swf", {
#           debug: false,
#           clip: {
#               url: videoclip_name_local,
#               debug: false,
#               provider: 'rtmp',
#               autoPlay: true,
#               autoBuffering: true,
#               onStart: function(){
#                   setPlayerControlState("active");
#                   videoclip_loaded = true;
#                   seekToChapter(videoclip_chapter_local);
#                   this.setVolume(100);
#                   this.unmute();
#               },
#               onCuepoint:[videoclip_chapters, function(clip, cuepoint){
#                   arrivedAtCuepoint(clip, cuepoint);
#               }]
#           },
#           plugins: {
#               rtmp: {
#                   url: media_url + "slidecasting-media/flowplayer/flowplayer.rtmp-3.2.12.swf",
#                   netConnectionUrl: videoclip_url_local //"rtmp://video.zserv.tuwien.ac.at/lecturetube_public" 
#               }
#           },
#           onError: function(){
#               setPlayerControlState("error");
#           }
#       });
#   }