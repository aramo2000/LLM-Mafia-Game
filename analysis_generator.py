from win_rates import calculate_win_rates_same, calculate_win_rates_different
from deception_detection import llms_deception_detection
from sentiment_readability import sentiment_analysis_dict, compact_sent_analysis_results
from sentiment_readability import readability_analysis_dict, compact_readability_analysis_results
from time_analysis import mafia_vs_civilian_response_times

from sentiment_readability import textblob_analysis_dict, compact_textblob_analysis_dict
from sentiment_readability import other_readability_analysis_dict, other_compact_readability_analysis_results
from sentiment_readability import vader_lexicon_analysis_dict, compact_vader_lexicon_analysis_dict
from sentiment_readability import nrc_emotion_aggregation_dict

# # generates win rate data for different llm types
# folder_name_different = "generated_data_different"
# json_name = "win_rates_different.json"
# calculate_win_rates_different(folder_name_different, json_name)

# # generates win rate data for same llm types
# folder_name_same = "generated_data_same"
# json_name = "win_rates_same.json"
# calculate_win_rates_same(folder_name_same, json_name)


# # generates deception and detection rates for different llm types
# folder_name = "generated_data_different"
# output_file = "deception_detection_different.json"
# llms_deception_detection(folder_name, output_file)

# # generates deception and detection rates for same llm types
# folder_name = "generated_data_same"
# output_file = "deception_detection_same.json"
# llms_deception_detection(folder_name, output_file)


# # generates sentiment analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "sentiment_analysis_different.json"
# sent_analysis_dict = sentiment_analysis_dict(folder_name, output_file)
# output_file = "compact_sentiment_analysis_different.json"
# compact_sent_analysis_results(sent_analysis_dict, output_file)

# # generates sentiment analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "sentiment_analysis_same.json"
# sent_analysis_dict = sentiment_analysis_dict(folder_name, output_file)
# output_file = "compact_sentiment_analysis_same.json"
# compact_sent_analysis_results(sent_analysis_dict, output_file)


# generates readability analysis results for different llm types
folder_name = "generated_data_different"
output_file = "sentiment_readability_analysis_data/readability_analysis_different.json"
readability_analysis_dic = readability_analysis_dict(folder_name, output_file)
output_file = "understandable_sentiment_readability/compact_readability_analysis_different.json"
compact_readability_analysis_results(readability_analysis_dic, output_file)

# generates readability analysis results for same llm types
folder_name = "generated_data_same"
output_file = "sentiment_readability_analysis_data/readability_analysis_same.json"
readability_analysis_dic = readability_analysis_dict(folder_name, output_file)
output_file = "understandable_sentiment_readability/compact_readability_analysis_same.json"
compact_readability_analysis_results(readability_analysis_dic, output_file)


# # generates time analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "analysis_data/time_analysis_different.json"
# mafia_vs_civilian_response_times(folder_name, output_file)

# # generates time analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "analysis_data/time_analysis_same.json"
# mafia_vs_civilian_response_times(folder_name, output_file)


# # generates fog smog analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "fog_smog_readability_analysis_different.json"
# readability_analysis_dic = other_readability_analysis_dict(folder_name, output_file)
# output_file = "compact_fog_smog_readability_analysis_different.json"
# other_compact_readability_analysis_results(readability_analysis_dic, output_file)

# # generates fog smog analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "fog_smog_other_readability_analysis_same.json"
# readability_analysis_dic = other_readability_analysis_dict(folder_name, output_file)
# output_file = "compact_fog_smog_readability_analysis_same.json"
# other_compact_readability_analysis_results(readability_analysis_dic, output_file)


# # generates textblob analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "blob_analysis_different.json"
# blob_analysis = textblob_analysis_dict(folder_name, output_file)
# output_file = "compact_blob_analysis_different.json"
# compact_textblob_analysis_dict(blob_analysis, output_file)

# # generates textblob analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "blob_analysis_same.json"
# blob_analysis = textblob_analysis_dict(folder_name, output_file)
# output_file = "compact_blob_analysis_same.json"
# compact_textblob_analysis_dict(blob_analysis, output_file)


# # generates vader lexicon analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "vader_analysis_different.json"
# vader_analysis = vader_lexicon_analysis_dict(folder_name, output_file)
# output_file = "compact_vader_analysis_different.json"
# compact_vader_lexicon_analysis_dict(vader_analysis, output_file)

# # generates vader lexicon analysis results for same llm types
# folder_name = "generated_data_same"
# output_file = "vader_analysis_same.json"
# vader_analysis = vader_lexicon_analysis_dict(folder_name, output_file)
# output_file = "compact_vader_analysis_same.json"
# compact_vader_lexicon_analysis_dict(vader_analysis, output_file)

# # generates emotion lexicon analysis results for different llm types
# folder_name = "generated_data_different"
# output_file = "analysis_data/emotions_analysis_different.json"
# emotions_analysis = nrc_emotion_aggregation_dict(folder_name, output_file)
