# Failure analysis: Groq (qwen/qwen3.8-27b) zero-shot, 53 errors

Buckets assigned by hand after reading every error. `ds` / `nv` = what DeepSeek and Nemotron (zero-shot) answered. ⚑ = gold label I'd disagree with.

| Bucket | Meaning | Count |
|---|---|---|
| A | Takes a side; gold ignores the stance | 16 |
| B | Bad news in a flat, factual tone | 9 |
| C | Factual / promo: unclear neutral vs positive | 10 |
| D | Sarcasm, irony, humour | 8 |
| E | Mixed sentiment in one tweet | 4 |
| F | Missing context, truncated or garbled | 6 |

## A. Takes a side; gold ignores the stance (16)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 1296 | neutral | negative | neutral | negative | Where were they during the height of Obama's Admin? |
| 3648 | neutral | negative | negative | negative | Quote this every time the Kremlin & pro-Putin media propagandists claim that #US troops are threatening Russia.… |
| 3773 | neutral | negative | neutral | negative | @user If evolution is bullshit then how do we develop vaccines???? |
| 4441 | neutral | negative | negative | negative | @user Obama Admin. asked them to look at alternate routes. Too little too late, the pipe is nearly at the riverbank. |
| 10598 | neutral | negative | negative | negative | @user @user Comey Must be on tRumps payroll. That would explain a lot! ⚑ *accusation with mocking 'tRump', so negative* |
| 10703 | neutral | negative | neutral | negative | @user @user  WE could add Henry Kissinger the Rothschild's, the Rockefeller's & George Soros ! |
| 10719 | neutral | negative | neutral | negative | IMPORTANT MUST DO: @user @user MUST Withdraw From Climate Convention. MUST READ:  @user |
| 10790 | neutral | negative | negative | negative | Stop animal testing #worldwide |
| 11185 | neutral | negative | negative | negative | @user Tony romo needs a new team lol |
| 11614 | neutral | negative | negative | negative | AMERICA controlled by KGB moles?No White House, but Red House?Demand the Popular Vote no Electoral Vote!SAVE THE USA NOW! |
| 1100 | neutral | positive | neutral | neutral | Please sign this petition to get aid to Aleppo...thnak you x |
| 1151 | neutral | positive | positive | positive | Yes, including Medicare and social security saving👍 ⚑ *'Yes' + 👍 is approval, so positive* |
| 4093 | neutral | positive | neutral | positive | @user true  go nigel go i stay with brexit and now i hope early italyexit |
| 9363 | neutral | positive | neutral | positive | Here's hoping Victoria heeds the call this week. #assisteddying #voluntary #euthanasia |
| 10948 | neutral | positive | neutral | positive | Getting ready for European Tour 2017! With support from @user and the #Trumptards! #MAGA #MERA… |
| 5045 | positive | negative | negative | negative | Walton family earns more than 130 million Americans - and food stamps and Medicaid funds used to subsidize its low wage earners ⚑ *critical of the Waltons, so negative* |

## B. Bad news in a flat, factual tone (9)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 3488 | neutral | negative | negative | negative | The Great Mexican Wall Deception: Trump's America Already Exists on the Border @user |
| 3861 | neutral | negative | neutral | negative | Liam Neeson steps down from Ballymena boxing club amid abortion row over narration of @user video @user |
| 5288 | neutral | negative | negative | negative | Alt-Right Conference Attendees Openly Use Nazi Salute, Language During Conference |
| 5439 | neutral | negative | neutral | negative | 18 Yezidi\|s have fled ISIS in Tal Afar, among them women, West of #Mosul.. #MosulOffensive |
| 6679 | neutral | negative | negative | negative | Pope Francis calls for end of Protestant Church via @user |
| 6782 | neutral | negative | neutral | negative | @user needed affirmation after being dumped#uitvnews #AshleyGrahamhttps://t.co/gDqZtpzXF3 |
| 9769 | neutral | negative | neutral | negative | #Daesh has called on its militants to travel to #Libya, Sinai in #Egypt, #Yemen, Khorasan & West Africa if they are unable to reach #Iraq |
| 11682 | neutral | negative | negative | negative | HHS nominee Tom Price belongs to Drs. group which believes vaccines cause autism & Obama care is socialized medicine. |
| 12187 | neutral | negative | negative | negative | @user @user @user @user @user @user Non-availablity of child vaccines @ Jamui, Bihar hospital** |

## C. Factual / promo: unclear neutral vs positive (10)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 1307 | neutral | positive | positive | positive | Dance Teacher Realness with my 10th grade girls #mannequinchallenge |
| 2334 | neutral | positive | neutral | positive | .@repjohnlewis #NBAwards acceptance speech has been viewed over 1.6 million times at @user |
| 2831 | neutral | positive | neutral | positive | Since becoming Barça coach in 2014, Luis Enrique has now given first team debuts to 11 players from the B team.… |
| 5275 | neutral | positive | neutral | positive | My #GilmoreGirlsTop4 1-Emily2-Paris3-Luke4-Babette The BFs are a given so they don't count |
| 6374 | neutral | positive | neutral | positive | Celebrity crush? — ashley graham and salma hayek |
| 9440 | neutral | positive | neutral | positive | @user @user Giving thanks on the corner of @user street -   #p2 #UniteBlue |
| 5157 | positive | neutral | neutral | neutral | . @user is going to be on @user tomorrow. #GilmoreGirlsTop4 |
| 5523 | positive | neutral | neutral | neutral | @user An article that may interest you re. 3D printing of crystal structures @user |
| 8878 | positive | neutral | neutral | positive | Samuel Umtiti working on his recovery. #fcblive |
| 10706 | positive | neutral | neutral | neutral | Random photos from #NBAwards, mostly of poetry judges and poets. |

## D. Sarcasm, irony, humour (8)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 921 | neutral | negative | neutral | neutral | Trump's wall on the Mexican border is just copying what Dhul-Qarnayn did to the Yajjuj Majjuj. #islamicmythologyjokes |
| 1178 | neutral | negative | negative | negative | if Persona 5 is already out and ready in Japan why can't we have it nowpleasemy crops are dying |
| 3507 | neutral | negative | negative | negative | @user @user @user And deplorables are a minority!  Glad that they feel they can come into the light. We see them. |
| 9606 | neutral | negative | negative | negative | @user @user @user expect a lot this from the revered wwc when Medicare gets flushed |
| 11597 | neutral | positive | neutral | negative | @user @user @user @user You haven't missed a thing by not watching @user |
| 11963 | neutral | positive | neutral | neutral | @user @user And Melania trump wrote her own speech |
| 1654 | positive | negative | neutral | negative | so my grandpa got medical marijuana and I think he's addicted:') |
| 3359 | positive | neutral | neutral | neutral | Just trying to imagine this was real...Those must have been some huge suitcases haha#Iran #Israel #Hezbollah |

## E. Mixed sentiment in one tweet (4)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 1856 | negative | positive | neutral | positive | @user @user Let us give thanks to recounts and the end of the alt-right Nazi's... |
| 8233 | negative | positive | negative | negative | my family was lit as hell when Chavez  died & it's a celebration now that Castro died & we not even Cuban...maduro when's your turn? |
| 4481 | neutral | negative | negative | negative | @user @user This is Hillary being vindictive.  Meanwhile, Trump's transition is going well. |
| 10286 | neutral | positive | neutral | positive | BÄÄÄÄM I love it 😊 what a bunch of assholes 😂😂 @user #thewalkingdead #normanreedus… |

## F. Missing context, truncated or garbled (6)

| id | gold | groq | ds | nv | tweet |
|---|---|---|---|---|---|
| 4449 | negative | neutral | neutral | negative | @user @user @user @user have you seen these fake stories attributed to you? ?? |
| 5462 | negative | neutral | neutral | neutral | @user My view is of course we can't reverse tech that will kill jobs like new self driving cars. But I think that manufacturing (1/2) |
| 9414 | negative | neutral | neutral | neutral | North SF Bay Leftists, Where Art Thou? (New Sub: /r/SFNorthBayAnarchists) |
| 9365 | negative | positive | negative | negative | ricky martin csn fuck with a steak knife i would tahnk him |
| 2701 | neutral | negative | neutral | negative | Like Grayson Allen, Adam is now operating at 50 percent. |
| 9939 | positive | neutral | neutral | neutral | I watched some Christmas goodies and ventured to showtime.  "Michael Moore in Trumpland"On of the first quotes?... |
